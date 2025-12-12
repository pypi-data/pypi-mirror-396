###############################################################################
# (c) Copyright 2023 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import annotations

from typing import Any

from DIRAC import gLogger
from DIRAC.Core.Utilities.ReturnValues import DReturnType, returnValueOrRaise, convertToReturnValue
from .FileQueryUtils import TableJoins, buildQuery, buildQueryInner, combineDescription, TABLE_JOIN_TO_NAME


GETFILESWITHMETADATA_AVAILABLE_COLUMNS = {
    "filename": None,
    "eventstat": None,
    "filesize": None,
    "creationdate": None,
    "jobstart": TableJoins.JOBS,
    "jobend": TableJoins.JOBS,
    "workernode": TableJoins.JOBS,
    "name": TableJoins.FILETYPES,
    "runnumber": TableJoins.JOBS,
    "fillnumber": TableJoins.JOBS,
    "fullstat": None,
    "dataqualityflag": TableJoins.DATAQUALITY,
    "eventinputstat": TableJoins.JOBS,
    "totalluminosity": TableJoins.JOBS,
    "luminosity": None,
    "instluminosity": None,
    "tck": TableJoins.JOBS,
    "guid": None,
    "adler32": None,
    "eventtypeid": None,
    "md5sum": None,
    "visibilityflag": None,
    "jobid": TableJoins.JOBS,
    "gotreplica": None,
    "inserttimestamp": None,
}

GETFILESWITHMETADATA_NAME_TO_COL = {
    "FileName": "filename",
    "EventStat": "eventstat",
    "FileSize": "filesize",
    "CreationDate": "creationdate",
    "JobStart": "jobstart",
    "JobEnd": "jobend",
    "WorkerNode": "workernode",
    "FileType": "name",
    "RunNumber": "runnumber",
    "FillNumber": "fillnumber",
    "FullStat": "fullstat",
    "DataqualityFlag": "dataqualityflag",
    "EventInputStat": "eventinputstat",
    "TotalLuminosity": "totalluminosity",
    "Luminosity": "luminosity",
    "InstLuminosity": "instluminosity",
    "TCK": "tck",
    "GUID": "guid",
    "ADLER32": "adler32",
    "EventType": "eventtypeid",
    "MD5SUM": "md5sum",
    "VisibilityFlag": "visibilityflag",
    "JobId": "jobid",
    "GotReplica": "gotreplica",
    "InsertTimeStamp": "inserttimestamp",
}


class NewOracleBookkeepingDB:
    def __init__(self, *, dbW, dbR):
        self.log = gLogger.getSubLogger("LegacyOracleBookkeepingDB")
        self.dbW_ = dbW
        self.dbR_ = dbR

    def getAvailableFileTypes(self) -> DReturnType[list[str]]:
        """Retrieve all available file types from the database."""
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getAvailableFileTypes", [])

    @convertToReturnValue
    def getProductionProducedEvents(self, prodid) -> int:
        """Retrieve number of produced events for given production.

        :param int prodid: production identifier
        :returns: number of produced events
        """
        # The basic idea behind this query is that for the majority of large
        # transformations, notably MC(Fast)?Simulation), there is only one step
        # therefore there is no need to join on the jobs table to figure out
        # the step a file belongs to.
        # To achieve this we use a common table expression (CTE) to gather the
        # count of steps for the production and then use a CROSS JOIN + UNION ALL
        # to effective do "if num_steps == 1 then do fast path else do standard path".
        # The step_info CTE ends up returning something like this:
        #     | production | stepid | rev_idx | num_steps |
        #     |------------|--------|---------|-----------|
        #     |    1234    |   56   |    1    |     3     |
        #     |    1234    |   57   |    2    |     3     |
        #     |    1234    |   58   |    3    |     3     |
        # So if num_steps == 1 the CROSS JOIN is a noop.
        # If num_steps > 1 we filter to only get the last step (rev_idx == 1)
        query = (
            "WITH step_info AS (\n"
            "    SELECT \n"
            "        production,\n"
            "        stepid,\n"
            # NOTE: ORDER BY step DESC i.e. rev_idx == 1 is the LAST step or max(step)
            "        ROW_NUMBER() OVER (PARTITION BY production ORDER BY step DESC) as rev_idx,\n"
            "        COUNT(*) OVER (PARTITION BY production) as num_steps\n"
            "    FROM stepscontainer\n"
            "    WHERE production = :prodid\n"
            "),\n"
            "ignored_filetypes AS (\n"
            "    SELECT FILETYPEID FROM FILETYPES WHERE NAME = 'LOG' OR NAME LIKE '%HIST%'"
            ")\n"
            # Fast path: single step production (no jobs join needed)
            "SELECT SUM(COALESCE(total, 0)) as total FROM (\n"
            "  SELECT SUM(f.eventstat) as total\n"
            "    FROM files f\n"
            "    CROSS JOIN (SELECT num_steps FROM step_info WHERE ROWNUM = 1) si\n"
            "    WHERE f.production = :prodid \n"
            # If we take the fast path, we need to exclude filetypes like LOG/HIST
            "      AND f.filetypeid NOT IN (SELECT filetypeid FROM ignored_filetypes) \n"
            "      AND si.num_steps = 1\n"
            "  UNION ALL\n"
            # Standard path: multi-step production
            "  SELECT SUM(f.eventstat) as total\n"
            "    FROM files f\n"
            "    JOIN jobs j ON j.jobid = f.jobid AND f.production = j.production\n"
            "    JOIN step_info si ON j.production = si.production AND j.stepid = si.stepid\n"
            "    WHERE j.production = :prodid \n"
            "      AND si.rev_idx = 1\n"
            "      AND si.num_steps > 1"
            ")"
        )
        result = returnValueOrRaise(self.dbR_.query(query, kwparams={"prodid": prodid}))
        if len(result) != 1 or len(result[0]) != 1:
            raise NotImplementedError(f"Unexpected result from produced events query {result}")
        if result and result[0][0] is not None:
            return result[0][0]
        return 0

    @convertToReturnValue
    def dumpRunDataQuality(self, configName: str, configVersion: str, eventType: int | None):
        """Retrieve all available data quality flags from the database."""
        query = (
            "SELECT DISTINCT j.fillnumber, j.runnumber, j.totalluminosity, dq.dataqualityflag, f.eventtypeid "
            "FROM files f "
            "JOIN jobs j ON f.production = j.production AND f.jobid = j.jobid "
            "JOIN dataquality dq ON f.qualityid = dq.qualityid "
            "JOIN configurations c ON c.configurationid = j.configurationid "
            "WHERE j.production < 0 AND c.configname = :configname AND c.configversion = :configversion"
        )
        kwparams = {"configname": configName, "configversion": configVersion}
        if eventType is not None:
            query += " AND f.eventtypeid = :eventtype"
            kwparams["eventtype"] = eventType
        result = returnValueOrRaise(self.dbR_.query(query, kwparams=kwparams))
        result = [(fill, run, lumi, dq, et) for fill, run, lumi, dq, et in result]
        return {
            "Records": result,
            "ParameterNames": ["FillNumber", "RunNumber", "TotalLuminosity", "DataQualityFlag", "EventType"],
            "TotalRecords": len(result),
        }

    @convertToReturnValue
    def getFileTypesForProdID(self, prodID: int) -> list[str]:
        query_parts = [
            "SELECT DISTINCT filetypes.name",
            "FROM files, jobs, filetypes",
            "WHERE files.jobid = jobs.jobid AND jobs.production = :prodid AND filetypes.filetypeid = files.filetypeid",
        ]
        result = returnValueOrRaise(self.dbR_.query(" ".join(query_parts), kwparams={"prodid": prodID}))
        return [ft for ft, in result]

    @convertToReturnValue
    def getAvailableSMOG2States(self) -> list[str]:
        """Retrieve all available SMOG2 states."""
        result = returnValueOrRaise(self.dbR_.query("SELECT state FROM smog2"))
        return [state for state, in result]

    @convertToReturnValue
    def getRunsForSMOG2(self, state: str) -> list[int]:
        """Retrieve all runs with specified SMOG2 state

        :param str state: required state
        """
        query = "SELECT runs.runnumber FROM smog2 LEFT JOIN runs ON runs.smog2_id = smog2.id WHERE smog2.state = :state"
        result = returnValueOrRaise(self.dbR_.query(query, kwparams={"state": state}))
        return [run for run, in result]

    def setSMOG2State(self, state: str, update: bool, runs: list[int]) -> DReturnType[None]:
        """Set SMOG2 state for runs.

        :param str state: state for given runs
        :param bool update: when True, updates existing state, when False throw an error in such case
        :param list[int] runs: runs list
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.setSMOG2", parameters=[state, update], output=False, array=runs
        )

    def setExtendedDQOK(self, run: int, update: bool, dqok: list[str]) -> DReturnType[None]:
        """Set ExtendedDQOK for specified run and systems. In case update is allowed,
        not specified systems are unset for the run.

        :param int run: run number for which systems are specified
        :param bool update: when True, updates existing set, when False throw an error in such case
        :param list[str] dqok: list of system names
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.setExtendedDQOK", parameters=[run, update, dqok], output=False
        )

    @convertToReturnValue
    def getRunsWithExtendedDQOK(self, dqok: list[str]) -> list[int]:
        """Retrieve all runs with specified systems in ExtendedDQOK
        NOTE: it is NOT checking quality is set to OK, so it should NOT be used
        for end user operations.

        :param list[str] dqok: systems
        """
        if not dqok:
            return []
        sql = ["SELECT ok.runnumber FROM extendeddqok ok"]
        params = {"sysname0": dqok[0]}
        for i, system in enumerate(dqok[1::]):
            sql.append(
                f"INNER JOIN extendeddqok ok{i} ON ok{i}.runnumber = ok.runnumber AND ok{i}.systemname = :sysname{i}"
            )
            params[f"sysname{i}"] = system
        sql.append("WHERE ok.systemname = :sysname0")
        result = returnValueOrRaise(self.dbR_.query(" ".join(sql), kwparams=params))
        return [run for run, in result]

    @convertToReturnValue
    def getRunExtendedDQOK(self, runnb: int) -> list[str]:
        """Return the list of systems in ExtendedDQOK for given run

        :param int runnb: run number
        """
        query = "SELECT systemname FROM extendeddqok WHERE runnumber = :run"
        result = returnValueOrRaise(self.dbR_.query(query, kwparams={"run": runnb}))
        return [sysname for sysname, in result]

    @convertToReturnValue
    def getAvailableExtendedDQOK(self) -> list[str]:
        """Retrieve all available Extended DQOK systems."""
        result = returnValueOrRaise(self.dbR_.query("select distinct systemname from extendeddqok"))
        return [systemname for systemname, in result]

    @convertToReturnValue
    def getListOfRunsInProd(self, prod_id) -> list[int]:
        query = "SELECT DISTINCT j.runnumber FROM jobs j WHERE j.production = :prod_id"
        result = returnValueOrRaise(self.dbR_.query(query, kwparams={"prod_id": prod_id}))
        return [run for run, in result]

    @convertToReturnValue
    def getInputOutputFilesForProd(self, prod_id, run_number):
        query_parts = [
            "SELECT f2.filename aname, f.filename dname, f.gotreplica, dt.name dtype",
            "FROM jobs j",
            "LEFT JOIN files f ON j.jobid = f.jobid AND j.production = f.production",
            "LEFT JOIN filetypes dt ON dt.filetypeid = f.filetypeid",
            "LEFT JOIN inputfiles i ON i.jobid = j.jobid",
            "LEFT JOIN files f2 ON i.fileid = f2.fileid",
            "where j.production = :prod_id",
        ]
        kwparams = {"prod_id": prod_id}
        if run_number is not None:
            query_parts.append("AND j.runnumber = :run_number")
            kwparams["run_number"] = run_number
        result = returnValueOrRaise(self.dbR_.query("\n".join(query_parts), kwparams=kwparams))
        return {
            "Records": result,
            "ParameterNames": ["AncestorLFN", "DescendantLFN", "GotReplica", "FileType"],
            "TotalRecords": len(result),
        }

    @convertToReturnValue
    def getOutputDescendantsForProd(self, prod_id, run_number):
        query_parts = [
            "SELECT f.filename AS aname,",
            "    f2.filename AS dname,",
            "    f2.gotreplica,",
            "    ft2.name",
            "FROM jobs j",
            "LEFT JOIN files f ON j.jobid = f.jobid AND j.production = f.production",
            "INNER JOIN inputfiles i ON i.fileid = f.fileid",
            "LEFT JOIN jobs j2 ON j2.jobid = i.jobid",
            "LEFT JOIN files f2 ON j2.jobid = f2.jobid AND j2.production = f2.production",
            "LEFT JOIN filetypes ft2 ON ft2.filetypeid = f2.filetypeid",
            "WHERE j.production = :prod_id",
        ]
        kwparams = {"prod_id": prod_id}
        if run_number is not None:
            query_parts.append("AND j.runnumber = :run_number")
            kwparams["run_number"] = run_number
        result = returnValueOrRaise(self.dbR_.query("\n".join(query_parts), kwparams=kwparams))
        return {
            "Records": result,
            "ParameterNames": ["AncestorLFN", "DescendantLFN", "GotReplica", "FileType"],
            "TotalRecords": len(result),
        }

    def _collectFileDescendents(
        self, lfns: list[str], depth: int, production: int, checkreplica: bool, tree: bool
    ) -> dict:
        """collects descendents for specified ancestors

        :param list lfns: a list of LFNs (ancestors)
        :param int depth: the depth of the processing pass chain(how far to go)
        :param productin: production number, when not zero, search descendats in that production only
        :param bool checkreplica: when set, returned descendents should have a replica
        :param bool tree: return direct ancestors relations when true
        :returns: descendent relations and metadata
        """
        # max number of lfns to process in one query, should be less then 1000 (with current implementation)
        block_size = 100
        # allowed depth range as in original version
        depth = min(10, max(1, depth))

        processed = dict.fromkeys(lfns, False)  # to detect "NotProcessed"
        dfiles = {lfn: {} for lfn in lfns}  # requested ancestors are always included
        metadata = {}

        sql_fields = [
            f"{'PRIOR' if tree else 'CONNECT_BY_ROOT'} f.filename aname",
            "f.filename dname",
            "f.gotreplica",
            "f.eventstat",
            "f.eventtypeid",
            "f.luminosity",
            "f.instluminosity",
            "dt.name dtype",
            "f.production" if tree or production != 0 else "0",
        ]
        sql_fields = ", ".join(sql_fields)

        sql_joins = [
            "LEFT JOIN inputfiles i ON i.fileid = f.fileid",
            "LEFT JOIN filetypes dt ON dt.filetypeid = f.filetypeid",
        ]
        sql_joins = " ".join(sql_joins)

        sql_where = f"LEVEL > 1 AND LEVEL < {depth+2}"  # LEVEL 1 is ancestor, depth is inclusive
        sql_connect = "PRIOR i.jobid = f.jobid"

        block_idx = 0
        while True:
            block_lfns = lfns[block_idx : block_idx + block_size :]
            if not block_lfns:
                break
            block_idx += block_size  # for the next block
            # bind as proposed in https://python-oracledb.readthedocs.io/en/latest/user_guide/bind.html , 7.13
            sql_start = "f.filename IN (" + ",".join([f":{i}" for i in range(1, len(block_lfns) + 1)]) + ")"

            sql = (
                f"SELECT {sql_fields} FROM files f {sql_joins} WHERE {sql_where}"
                f" START WITH {sql_start} CONNECT BY {sql_connect}"
            )
            result = returnValueOrRaise(self.dbR_.query(sql, params=[block_lfns]))
            for aname, dname, gotreplica, eventstat, eventtype, lumi, instlumi, dtype, prod in result:
                if aname in processed:  # for tree == true case
                    processed[aname] = True  # mimic previous behaviour ("processed" if there is any descendant)
                if (not checkreplica or (gotreplica != "No")) and (
                    tree or (prod == production)
                ):  # always true for tree version, salso works correctly for production == 0
                    if aname not in dfiles:  # can happened when tree == true
                        dfiles[aname] = {}
                    dfiles[aname][dname] = {}
                    metadata[dname] = {
                        "GotReplica": gotreplica,
                        "EventStat": eventstat,
                        "EventType": eventtype,
                        "Luminosity": lumi,
                        "InstLuminosity": instlumi,
                        "FileType": dtype,
                    }
                    if tree:
                        metadata[dname]["Production"] = prod

        return processed, dfiles, metadata

    @convertToReturnValue
    def getFileDescendents(
        self, lfns: list[str], depth: int = 0, production: int = 0, checkreplica: bool = True
    ) -> dict:
        """collects descendents for specified ancestors

        :param list lfns: a list of LFNs (ancestors)
        :param int depth: the depth of the processing pass chain(how far to go)
        :param productin: production number, when not zero, search descendats in that production only
        :param bool checkreplica: when set, returned descendents should have a replica
        :returns: descendents and suplementary information
        """
        # AZ: original code never fail, it returns "Failed" list in case of problems with Oracle.
        #     So the behaviour is NOT identical when there are problems with Oracle
        # AZ: the order of files in lists of "Successful" is different from original (dictionary "WithMetadata" should match)
        if not lfns:
            return {"Failed": [], "NotProcessed": [], "Successful": {}, "WithMetadata": {}}
        processed, dfiles, metadata = self._collectFileDescendents(lfns, depth, production, checkreplica, False)
        return {
            "Failed": [],  # always emtpy (or error) in this implementation
            "NotProcessed": [lfn for lfn in lfns if not processed[lfn]],  # preserve original order
            "Successful": {lfn: list(dfiles[lfn]) for lfn in dfiles if processed[lfn]},
            "WithMetadata": {lfn: {dlfn: metadata[dlfn] for dlfn in dfiles[lfn]} for lfn in dfiles if processed[lfn]},
        }

    @convertToReturnValue
    def getFileDescendentsTree(self, lfns: list[str], depth: int = 0) -> dict:
        """collects descendents for specified ancestors

        :param list lfns: a list of LFNs (ancestors)
        :param int depth: the depth of the processing pass chain(how far to go)
        :returns: the tree of descendents and metadata (metadata include Production)
        """
        if not lfns:
            return {"descendents": {}, "metadata": {}}
        _, dfiles, metadata = self._collectFileDescendents(lfns, depth, 0, False, True)
        for lfn in dfiles:  # make the tree from direct descendents
            dfiles[lfn].update({dlfn: dfiles[dlfn] if dlfn in dfiles else {} for dlfn in dfiles[lfn]})
        return {"descendents": {lfn: dfiles[lfn] for lfn in lfns}, "metadata": metadata}

    @convertToReturnValue
    def getFiles(
        self,
        simdesc,
        datataking,
        procPass,
        ftype,
        evt,
        configName="ALL",
        configVersion="ALL",
        production="ALL",
        flag="ALL",
        startDate=None,
        endDate=None,
        nbofEvents=False,
        startRunID=None,
        endRunID=None,
        runnumbers=None,
        replicaFlag="ALL",
        visible="ALL",
        filesize=False,
        tcks=None,
        jobStart=None,
        jobEnd=None,
        smog2States=None,
        dqok=None,
        seed_md5=None,
        sample_max=None,
    ):
        if nbofEvents:
            selection = "SUM(f.eventstat)"
        elif filesize:
            selection = "SUM(f.filesize)"
        else:
            # TODO: Ideally DISTINCT shouldn't be needed here but we should
            # probably add a unique constraint to the DB before removing it.
            # Actually, the previous two queries don't consider the DISTINCT
            # so if it's needed here those queries are incorrect.
            selection = "DISTINCT f.filename"

        return buildQuery(
            self.dbR_,
            selection,
            combineDescription(simdesc, datataking),
            procPass,
            ftype,
            evt,
            configName,
            configVersion,
            production,
            flag,
            startDate,
            endDate,
            startRunID,
            endRunID,
            runnumbers,
            replicaFlag,
            visible,
            tcks,
            jobStart,
            jobEnd,
            smog2States,
            dqok,
            seed_md5,
            sample_max,
        )

    @convertToReturnValue
    def getFilesWithMetadata(
        self,
        configName,
        configVersion,
        conddescription="ALL",
        processing="ALL",
        evt="ALL",
        production="ALL",
        filetype="ALL",
        quality="ALL",
        visible="ALL",
        replicaflag="ALL",
        startDate=None,
        endDate=None,
        runnumbers=None,
        startRunID=None,
        endRunID=None,
        tcks="ALL",
        jobStart=None,
        jobEnd=None,
        selection=None,
        smog2States=None,
        dqok=None,
        seed_md5=None,
        sample_max=None,
        *,
        parameters=None,
    ):
        if selection is not None:
            raise NotImplementedError("Selection is not implemented")

        forceJoins = []
        if parameters is None:
            parameters = list(GETFILESWITHMETADATA_NAME_TO_COL)
        selection = []
        for parameter in parameters:
            col = GETFILESWITHMETADATA_NAME_TO_COL[parameter]
            join = GETFILESWITHMETADATA_AVAILABLE_COLUMNS[col]
            selection.append(f"{TABLE_JOIN_TO_NAME[join]}.{col}")
            if join is not None:
                forceJoins.append(join)

        return buildQuery(
            self.dbR_,
            ", ".join(selection),
            conddescription,
            processing,
            filetype,
            evt,
            configName,
            configVersion,
            production,
            quality,
            startDate,
            endDate,
            startRunID,
            endRunID,
            runnumbers,
            replicaflag,
            visible,
            tcks,
            jobStart,
            jobEnd,
            smog2States,
            dqok,
            seed_md5,
            sample_max,
            forceJoins=forceJoins,
            # FIXME: Arguably this is a bug but it's needed to reproduce the behaviour of the original code
            # After we've migrated to the new method we should probably remove this?
            extraConditions={"f.eventtypeid IS NOT NULL"},
        )

    @convertToReturnValue
    def getVisibleFilesWithMetadata(
        self,
        simdesc,
        datataking,
        procPass,
        ftype,
        evt,
        configName="ALL",
        configVersion="ALL",
        production="ALL",
        flag="ALL",
        startDate=None,
        endDate=None,
        nbofEvents=None,
        startRunID=None,
        endRunID=None,
        runnumbers=None,
        replicaFlag="Yes",
        tcks=None,
        jobStart=None,
        jobEnd=None,
        smog2States=None,
        dqok=None,
        seed_md5=None,
        sample_max=None,
    ):
        # These options are broken the in the original code
        if nbofEvents is not None:
            raise NotImplementedError("nbofEvents is not implemented for visible files")
        if replicaFlag != "Yes":
            raise NotImplementedError("This option is broken in the original code")

        selection = (
            "DISTINCT f.filename, f.eventstat, j.eventinputstat, j.runnumber, j.fillnumber, f.filesize, "
            "j.totalluminosity, f.luminosity, f.instLuminosity, j.tck"
        )
        return buildQuery(
            self.dbR_,
            selection,
            combineDescription(simdesc, datataking),
            procPass,
            ftype,
            evt,
            configName,
            configVersion,
            production,
            flag,
            startDate,
            endDate,
            startRunID,
            endRunID,
            runnumbers,
            replicaFlag,
            "Y",
            tcks,
            jobStart,
            jobEnd,
            smog2States,
            dqok,
            seed_md5,
            sample_max,
            forceJoins={TableJoins.JOBS},
        )

    @convertToReturnValue
    def getFilesSummary(
        self,
        configName,
        configVersion,
        conditionDescription="ALL",
        processingPass="ALL",
        eventType="ALL",
        production="ALL",
        fileType="ALL",
        dataQuality="ALL",
        startRun="ALL",
        endRun="ALL",
        visible="ALL",
        startDate=None,
        endDate=None,
        runNumbers=None,
        replicaFlag="ALL",
        tcks="ALL",
        jobStart=None,
        jobEnd=None,
        smog2States=None,
        dqok=None,
        seed_md5=None,
        sample_max=None,
    ):
        selection = "COUNT(fileid), SUM(f.EventStat), SUM(f.FILESIZE), SUM(f.luminosity), SUM(f.instLuminosity)"
        return buildQuery(
            self.dbR_,
            selection,
            conditionDescription,
            processingPass,
            fileType,
            eventType,
            configName,
            configVersion,
            production,
            dataQuality,
            startDate,
            endDate,
            startRun,
            endRun,
            runNumbers,
            replicaFlag,
            visible,
            tcks,
            jobStart,
            jobEnd,
            smog2States,
            dqok,
            seed_md5,
            sample_max,
        )

    @convertToReturnValue
    def listBookkeepingPaths(self, in_dict):
        """Data set summary.

        :param dict in_dict: bookkeeping query dictionary
        """
        parameterNames = [
            "Production",
            "EventType",
            "ConfigName",
            "ConfigVersion",
            "ProcessingPass",
            "ConditionDescription",
            "FileType",
        ]
        forceJoins = {
            TableJoins.CONDESC,
            TableJoins.CONFIGURATIONS,
            TableJoins.PRODUCTIONSCONTAINER,
            TableJoins.PROCPATHS,
            TableJoins.FILETYPES,
        }
        selection = (
            "distinct f.production, f.eventtypeid, c.configname, c.configversion, "
            "'/' || pp.procpath, cd.description, ft.name"
        )
        rows = buildQuery(
            self.dbR_,
            selection,
            None,
            None,
            None,
            in_dict.get("EventType"),
            in_dict.get("ConfigName"),
            in_dict.get("ConfigVersion"),
            in_dict.get("Production"),
            None,
            None,
            None,
            None,
            None,
            None,
            "Yes",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            forceJoins=forceJoins,
        )
        result = [dict(zip(parameterNames, row)) for row in rows]
        return [
            r
            for r in result
            # Exclude Analysis Production-like processing passes
            if "AnaProd" not in r["ProcessingPass"] and "CharmWGProd" not in r["ProcessingPass"]
        ]

    @convertToReturnValue
    def getFileAncestryForRequest(
        self,
        getFilesWithMetadataArgs: list[Any],
        getFilesWithMetadataKwargs: dict[str, Any],
        productions: list[tuple[int, str]],
    ):
        """Get file ancestry for a request defined by getFilesWithMetadataArgs and productions

        :param dict getFilesWithMetadataArgs: the list of arguments that would be
            equivalent to those passed to getFilesWithMetadata for the request's input query
        :param dict getFilesWithMetadataKwargs: the list of keyword arguments that would be
            equivalent to those passed to getFilesWithMetadata for the request's input query
        :param list productions: list of (production_id, filetype) tuples defining the productions to consider
        :returns: dictionary with ancestry information
        """
        # First find the expected input files for the request
        if not getFilesWithMetadataKwargs:
            getFilesWithMetadataKwargs = {"seed_md5": None, "sample_max": None}
        ctes, mainQuery, kwparams, pre_inserts = buildQueryInner(
            "NULL, f.jobid, f.fileid, f.filename, f.filesize, f.eventstat",
            *do_the_shuffle(*getFilesWithMetadataArgs),
            **getFilesWithMetadataKwargs,
            # FIXME: Arguably this is a bug but it's needed to reproduce the behaviour of the original code
            # After we've migrated to the new method we should probably remove this?
            extraConditions={"f.eventtypeid IS NOT NULL"},
        )
        ctes = sorted(ctes)

        # We're now going to put most of the logic into CTEs to make it easier to manage.
        # These are structured as follows where N is the index in the productions list (1-based):
        # qN: The expected input files to production N
        # qNi: The actual input files to production N (from ancestry of output files)
        # qNa: The combined expected/actual input files to production N
        # The final output is then a UNION ALL of all the qNa tables plus the expected files
        # for the last production (which have no actual input files).

        # Get the expected input files of the first production
        mainQuery = ["    " + line for line in mainQuery]
        mainQuery.insert(0, "q0 (production, jobid, fileid, lfn, filesize, n_events) as (")
        mainQuery.append(")")
        ctes.append("\n".join(mainQuery))

        # Now for each production, find the output files and their expected/actual input files
        for i, (prod_id, ftype) in enumerate(productions, start=1):
            kwparams[f"ft{i}"] = ftype
            kwparams[f"prod{i}"] = prod_id
            # Now find the output files of this production
            condition = f"ft.name = :ft{i} AND f.production = :prod{i}"
            if productions[-1] == (prod_id, ftype):
                # For the last production we only want files that have replicas
                condition += " AND f.replicaFlag = 'Yes'"
            ctes.append(
                f"q{i} (production, jobid, fileid, lfn, filesize, n_events) as (\n"
                f"    SELECT f.production, f.jobid, f.fileid, f.filename, f.filesize, f.eventstat\n"
                f"    FROM files f\n"
                f"    JOIN filetypes ft ON f.filetypeid = ft.filetypeid\n"
                f"    WHERE ft.name = :ft{i} AND f.production = :prod{i}\n"
                f")"
            )
            # Next the input files of the above output files using ancestry
            ctes.append(
                f"q{i}i (fileid, filename, filesize, n_events) as (\n"
                f"    SELECT f.fileid, f.filename, f.filesize, f.eventstat\n"
                f"    FROM FILES f\n"
                f"    JOIN inputfiles inf ON f.fileid = inf.fileid\n"
                f"    JOIN q{i} ON inf.jobid = q{i}.jobid\n"
                f")"
            )
            # Combine the ancestry information with the expected files, using FULL OUTER JOIN
            # to ensure we get all files even if they are only in one of the sets
            ctes.append(
                f"q{i-1}a (lfn, filesize, n_events, production, processed, expected) as (\n"
                f"    SELECT\n"
                f"        COALESCE(q{i-1}.lfn, q{i}i.filename) as lfn,\n"
                f"        COALESCE(q{i-1}.filesize, q{i}i.filesize) as filesize,\n"
                f"        COALESCE(q{i-1}.n_events, q{i}i.n_events) as n_events,\n"
                f"        COALESCE(q{i-1}.production, :prod{i}) as production,\n"
                f"        CASE WHEN q{i}i.fileid IS NOT NULL THEN 'Y' ELSE 'N' END as processed,\n"
                f"        CASE WHEN q{i-1}.fileid IS NOT NULL THEN 'Y' ELSE 'N' END as expected\n"
                f"    FROM q{i-1}\n"
                f"    FULL OUTER JOIN q{i}i ON q{i-1}.fileid = q{i}i.fileid\n"
                f")"
            )

        # Finally combine everything together with a UNION ALL
        unionParts = ["SELECT lfn, filesize, n_events, NULL, processed, expected FROM q0a"]
        for i in range(1, len(productions)):
            unionParts.append(f"SELECT lfn, filesize, n_events, production, processed, expected FROM q{i}a")
        # For the output files of the last production, there is no concept of "processed"
        # and "expected" to be processed so we just set them to NULL and select from qN directly
        unionParts.append(
            f"SELECT lfn, filesize, n_events, production, NULL as processed, NULL as expected FROM q{len(productions)}"
        )
        mainQuery = ["\nUNION ALL\n".join(unionParts)]

        # Finally we can assemble the full query
        query = []
        if ctes:
            query.append("WITH " + ", ".join(ctes))
        query.extend(mainQuery)
        return returnValueOrRaise(self.dbR_.query("\n".join(query), kwparams=kwparams, pre_inserts=pre_inserts))


def do_the_shuffle(
    configName,
    configVersion,
    conddescription="ALL",
    processing="ALL",
    evt="ALL",
    production="ALL",
    filetype="ALL",
    quality="ALL",
    visible="ALL",
    replicaflag="ALL",
    startDate=None,
    endDate=None,
    runnumbers=None,
    startRunID=None,
    endRunID=None,
    tcks="ALL",
    jobStart=None,
    jobEnd=None,
    selection=None,
    smog2States=None,
    dqok=None,
):
    return (
        conddescription,
        processing,
        filetype,
        evt,
        configName,
        configVersion,
        production,
        quality,
        startDate,
        endDate,
        startRunID,
        endRunID,
        runnumbers,
        replicaflag,
        visible,
        tcks,
        jobStart,
        jobEnd,
        smog2States,
        dqok,
    )
