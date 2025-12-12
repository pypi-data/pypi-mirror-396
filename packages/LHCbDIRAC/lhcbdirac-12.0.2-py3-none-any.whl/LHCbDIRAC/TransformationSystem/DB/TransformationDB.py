###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""DIRAC Transformation DB.

Transformation database is used to collect and serve the necessary
information in order to automate the task of job preparation for high
level transformations. This class is typically used as a base class for
more specific data processing databases
"""
# Disable it because pylint does not understand decorator (convertToReturnValue)

# pylint: disable=invalid-sequence-index

import json
import threading
import copy
import re
from collections import defaultdict

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.TransformationSystem.DB.TransformationDB import TransformationDB as DIRACTransformationDB
from DIRAC.Core.Utilities.List import intListToString, breakListIntoChunks
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise


class TransformationDB(DIRACTransformationDB):
    """Extension of the DIRAC Transformation DB."""

    def __init__(self, dbname=None, dbconfig=None, dbIn=None, parentLogger=None):
        """The standard constructor takes the database name (dbname) and the name
        of the configuration section (dbconfig)"""
        DIRACTransformationDB.__init__(self, dbname, dbconfig, dbIn, parentLogger=parentLogger)
        self.lock = threading.Lock()
        self.queryFields = (
            "SimulationConditions",
            "DataTakingConditions",
            "ProcessingPass",
            "FileType",
            "EventType",
            "ConfigName",
            "ConfigVersion",
            "ProductionID",
            "DataQualityFlag",
            "ExtendedDQOK",
            "SMOG2",
            "StartRun",
            "EndRun",
            "EndDate",
            "Visible",
            "RunNumbers",
            "TCK",
            "SampleSeedMD5",
            "SampleMax",
        )
        self.intFields = ("EventType", "ProductionID", "StartRun", "EndRun")
        self.transRunParams = ("TransformationID", "RunNumber", "SelectedSite", "Status", "LastUpdate")
        self.allowedStatusForTasks = ("Unused", "ProbInFC")
        self.TRANSPARAMS.append("Hot")
        self.TRANSFILEPARAMS.extend(["RunNumber", "Size", "FileType", "RAWAncestors"])
        self.TASKSPARAMS.append("RunNumber")

    def deleteTransformation(self, transID, author="", connection=False):
        """Small extension to not forget to delete the BkQueries."""
        res = self.deleteBookkeepingQuery(transID, connection)
        if not res["OK"]:
            return res

        return DIRACTransformationDB.deleteTransformation(self, transID, author, connection)

    def jobIDsForAssignedFiles(self, transID):
        """Get the job IDs for files in status 'Assigned' for the given transformation ID.

        This is primarily by the Analysis Productions monitoring page.
        """
        req = f"""
        SELECT tt.ExternalID
        FROM `TransformationTasks` tt
        INNER JOIN (
            SELECT DISTINCT TransformationID, TaskID
            FROM `TransformationFiles`
            WHERE `TransformationID` = {int(transID)} AND Status = 'Assigned'
        ) tf ON tt.TransformationID = tf.TransformationID
            AND tt.TaskID = tf.TaskID
        WHERE tt.ExternalID != '' AND tt.ExternalID != 0 AND tt.ExternalID IS NOT NULL
        ORDER BY tt.TransformationID, tt.ExternalID
        """
        res = self._query(req)
        if not res["OK"]:
            return res
        return S_OK([int(r) for r, in res["Value"]])

    def jobIDsForFilesInMaxReset(self, transID):
        """Get all task/job IDs for files in MaxReset for the given transformation ID.

        This will include all tasks that processed a given file and is primarily
        used by the Analysis Productions monitoring page.
        """
        req = f"""
        SELECT df.LFN, tft.TaskID, tt.ExternalID
        FROM `TransformationFileTasks` tft
        INNER JOIN `DataFiles` df ON tft.FileID = df.FileID
        INNER JOIN `TransformationTasks` tt ON tft.TransformationID = tt.TransformationID
                                        AND tft.TaskID = tt.TaskID
        WHERE tft.TransformationID = {int(transID)}
        AND tft.FileID IN (
            SELECT FileID
            FROM `TransformationFiles`
            WHERE `TransformationID` = {int(transID)}
                AND `Status` = 'MaxReset'
        )
        AND tt.ExternalID != ''
        AND tt.ExternalID != 0
        AND tt.ExternalID IS NOT NULL
        """
        res = self._query(req)
        if not res["OK"]:
            return res
        result = {}
        for lfn, taskID, externalID in res["Value"]:
            result.setdefault(lfn, []).append((int(taskID), int(externalID)))
        return S_OK(result)

    def cleanTransformation(self, transID, author="", connection=False):
        """Clean the transformation specified by name or id Extends DIRAC one for
        deleting the unused runs metadata."""
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        connection = res["Value"]["Connection"]

        # deleting runs metadata
        req = f"SELECT DISTINCT RunNumber FROM TransformationRuns WHERE TransformationID = {transID}"
        res = self._query(req)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        runsMaybeToDelete = [r[0] for r in res["Value"]]

        req = f"SELECT DISTINCT RunNumber FROM TransformationRuns WHERE TransformationID != {transID}"
        res = self._query(req)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        runsToKeep = [r[0] for r in res["Value"]]

        runIDsToBeDeleted = list(set(runsMaybeToDelete) - set(runsToKeep))

        if runIDsToBeDeleted:
            res = self.deleteRunsMetadata(
                {"RunNumber": runIDsToBeDeleted, "Name": ["TCK", "CondDb", "DDDB"]}, connection
            )
            if not res["OK"]:
                return res

        res = DIRACTransformationDB.cleanTransformation(self, transID, connection=connection)
        if not res["OK"]:
            return res

        res = self.removeStoredJobDescription(transID, connection=connection)
        if not res["OK"]:
            return res

        res = self.__cleanTransformationRuns(transID, connection=connection)
        if not res["OK"]:
            return res
        return S_OK(transID)

    def getTasksForSubmission(
        self, transID, numTasks=1, site="", statusList=["Created"], older=None, newer=None, connection=False
    ):
        """extends base class including the run metadata."""
        tasksDict = DIRACTransformationDB.getTasksForSubmission(
            self, transID, numTasks, site, statusList, older, newer, connection
        )
        if not tasksDict["OK"]:
            return tasksDict

        tasksDict = tasksDict["Value"]
        runNumbers = []
        for taskForSumbission in tasksDict.values():
            run = taskForSumbission.get("RunNumber")
            if run and run not in runNumbers:
                runNumbers.append(run)

        if runNumbers:
            runsMetadata = self.getRunsMetadata(runNumbers, connection)
            if not runsMetadata["OK"]:
                return runsMetadata

            runsMetadata = runsMetadata["Value"]
            for taskForSumbission in tasksDict.values():
                try:
                    taskForSumbission["RunMetadata"] = runsMetadata[taskForSumbission["RunNumber"]]
                except KeyError:
                    continue

        return S_OK(tasksDict)

    def setHotFlag(self, transID, flag=False, connection=False):
        """Simply set the hot flag."""
        connection = self.__getConnection(connection)
        return self._update(
            "UPDATE Transformations SET Hot = %s WHERE TransformationID = %d" % (flag, int(transID)), conn=connection
        )

    #############################################################################
    #
    # Managing the BkQueries table

    def deleteBookkeepingQuery(self, transID, connection=False):
        """Delete the specified query from the database."""
        connection = self.__getConnection(connection)
        return self._update("DELETE FROM BkQueriesNew WHERE TransformationID=%d" % int(transID), conn=connection)

    def setInputQueryParameter(self, transID, queryParam, queryValue, *, connection=False, author=""):
        """Set the input query parameter for the supplied transformation ID."""
        res = returnValueOrRaise(self._getConnectionTransID(connection, transID))
        connection = res["Connection"]

        res = returnValueOrRaise(self.getBookkeepingQuery(transID, connection=connection))
        oldValue = res.get(queryParam, None)
        if queryValue == oldValue:
            return S_OK(f"Parameter {queryParam} {queryValue=} already set")

        query = [
            "INSERT INTO BKQueriesNew (TransformationID,ParameterName,ParameterValue) ",
            "VALUES (%s, %s, %s) ",
            "ON DUPLICATE KEY UPDATE ParameterValue = %s",
        ]

        res = self._update(
            "\n".join(query),
            args=(transID, queryParam, queryValue, queryValue),
            conn=connection or None,
        )

        self.__updateTransformationLogging(
            transID,
            f"Updated BK {queryParam=} from {oldValue=} to {queryValue}",
            author=author,
            connection=connection,
        )

        return S_OK(res)

    def setBookkeepingQueryEndRun(self, transID, runNumber, connection=False):
        """Set the EndRun for the supplied transformation."""
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        connection = res["Value"]["Connection"]
        res = self.getBookkeepingQuery(transID, connection=connection)
        if not res["OK"]:
            return res
        startRun = res["Value"].get("StartRun")
        endRun = res["Value"].get("EndRun")
        if endRun and runNumber < endRun:
            return S_ERROR("EndRun can not be reduced!")
        if startRun and startRun > runNumber:
            return S_ERROR("EndRun is before StartRun!")
        req = (
            "INSERT INTO BkQueriesNew(TransformationID,ParameterName,ParameterValue) VALUES(%d,'EndRun',%d) \
    ON DUPLICATE KEY UPDATE ParameterValue = %d"
            % (transID, runNumber, runNumber)
        )
        return self._update(req, conn=connection)

    def setBookkeepingQueryStartRun(self, transID, runNumber, connection=False):
        """Set the StartRun for the supplied transformation."""
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        connection = res["Value"]["Connection"]
        res = self.getBookkeepingQuery(transID, connection=connection)
        if not res["OK"]:
            return res
        endRun = res["Value"].get("EndRun")
        startRun = res["Value"].get("StartRun")
        if startRun and runNumber > startRun:
            return S_ERROR("StartRun can not be increased!")
        if endRun and runNumber > endRun:
            return S_ERROR("StartRun cannot be after EndRun!")
        req = (
            "INSERT INTO BkQueriesNew(TransformationID,ParameterName,ParameterValue) VALUES(%d,'StartRun',%d) \
    ON DUPLICATE KEY UPDATE ParameterValue = %d"
            % (transID, runNumber, runNumber)
        )
        return self._update(req, conn=connection)

    def addBookkeepingQueryRunList(self, transID, runList, connection=False):
        """Adds the list of runs."""
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return S_ERROR("Failed to get Connection to TransformationDB")
        connection = res["Value"]["Connection"]
        res = self.getBookkeepingQuery(transID, connection=connection)
        if not res["OK"]:
            return S_ERROR("Cannot retrieve BkQuery")
        if "StartRun" in res["Value"] or "EndRun" in res["Value"]:
            return S_ERROR("RunList incompatible with start or end run")
        runsInQuery = set()
        try:
            runNumbers = res["Value"].get("RunNumbers", [])
            if runNumbers != "All":
                if not isinstance(runNumbers, list):
                    runNumbers = [runNumbers]
                runsInQuery = {int(run) for run in runNumbers}
            else:
                return S_ERROR("Cannot add runs to 'All'")
            runsInQuery |= {int(run) for run in runList}
        except ValueError as e:
            return S_ERROR(f"RunList invalid: {repr(e)}")
        if len(runsInQuery) > 999:
            return S_ERROR("RunList bigger the 1000 not allowed because of Oracle limitations!!!")
        value = ";;;".join(str(x) for x in sorted(runsInQuery))
        req = (
            "UPDATE BkQueriesNew SET ParameterValue='%s' WHERE TransformationID = %d AND ParameterName='RunNumbers'"
            % (value, transID)
        )
        self._update(req, conn=connection)
        return S_OK()

    def addBookkeepingQuery(self, transID, queryDict, connection=False):
        """Add a new Bookkeeping query specification."""
        connection = self.__getConnection(connection)
        values = []
        for field in self.queryFields:
            if field not in queryDict:
                if field in ["StartRun", "EndRun"]:
                    value = 0
                else:
                    value = "All"
            else:
                value = queryDict[field]

                if isinstance(value, (int,) + (float,)):
                    value = str(value)
                if isinstance(value, (list, tuple)):
                    value = ";;;".join(str(x) for x in value)
            values.append(value)

        # Insert the new bk query
        req = "INSERT INTO BkQueriesNew (TransformationID, ParameterName,ParameterValue) VALUES "
        for field, value in zip(self.queryFields, values):
            req += "(%d,'%s','%s'), " % (transID, field, value)
        req = req.strip().rstrip(",")

        res = self._update(req, conn=connection)
        if not res["OK"]:
            return res
        return S_OK(transID)

    def getTransformationsWithBkQueries(self, transIDs=None, connection=False):
        """Get those Transformations that have a BkQuery."""
        connection = self.__getConnection(connection)
        req = "SELECT DISTINCT TransformationID FROM BkQueriesNew"
        if transIDs:
            req = req + f" WHERE TransformationID IN ({', '.join(str(t) for t in transIDs)})"
        res = self._query(req, conn=connection)
        if res["OK"]:
            res = S_OK([tID[0] for tID in res["Value"]])
        return res

    def getBookkeepingQuery(self, transID, connection=False):
        """Get the bookkeeping query parameters."""
        result = self.getBookkeepingQueries([transID], connection)
        if result["OK"]:
            result["Value"] = result["Value"][transID]
        return result

    def getBookkeepingQueries(self, transIDs, connection=False):
        """Get the bookkeeping query parameters."""
        connection = self.__getConnection(connection)
        req = (
            "SELECT TransformationID, ParameterName, ParameterValue FROM BkQueriesNew "
            f"WHERE TransformationID IN ({', '.join(str(t) for t in transIDs)})"
        )
        res = self._query(req, conn=connection)
        if not res["OK"]:
            return res
        bkDict = defaultdict(dict)
        for row in res["Value"]:
            transID = row[0]
            parameter = row[1]
            value = row[2]
            if value and value != "All":
                if re.search(";;;", str(value)):
                    value = value.split(";;;")
                if parameter in self.intFields:
                    if isinstance(value, str):
                        value = int(value)
                    if isinstance(value, list):
                        value = [int(x) for x in value]
                    if not value:
                        continue
                bkDict[transID][parameter] = value
        for transID in transIDs:
            if transID not in bkDict:
                return S_ERROR("BkQuery %d not found" % int(transID))
        return S_OK(dict(bkDict))

    def __insertExistingTransformationFiles(self, transID, fileTuplesList, connection=False):
        """extends DIRAC.__insertExistingTransformationFiles Does not add userSE
        and adds runNumber."""

        gLogger.info(f"Inserting {len(fileTuplesList)} files in TransformationFiles")
        # splitting in various chunks, in case it is too big
        for fileTuples in breakListIntoChunks(fileTuplesList, 10000):
            gLogger.verbose(
                f"Adding first {len(fileTuples)} files in TransformationFiles (out of {len(fileTuplesList)})"
            )
            req = "INSERT INTO TransformationFiles (TransformationID,Status,TaskID,FileID, \
      TargetSE,LastUpdate,RunNumber,Size,FileType,RAWAncestors) VALUES"
            candidates = False

            for ft in fileTuples:
                (
                    _lfn,
                    originalID,
                    fileID,
                    status,
                    taskID,
                    targetSE,
                    _usedSE,
                    _errorCount,
                    _lastUpdate,
                    _insertTime,
                    runNumber,
                    size,
                    fileType,
                    rawAncestors,
                ) = ft[:14]
                if status not in ("Removed",):
                    candidates = True
                    if not re.search("-", status):
                        status = f"{status}-inherited"
                        if taskID:
                            taskID = 1000000 * int(originalID) + int(taskID)
                    req = "%s (%d,'%s',%s,%d,'%s',UTC_TIMESTAMP(),%s,%s,'%s',%s)," % (
                        req,
                        transID,
                        status,
                        taskID,
                        fileID,
                        targetSE,
                        runNumber,
                        size,
                        fileType,
                        rawAncestors,
                    )
            if not candidates:
                continue
            req = req.rstrip(",")
            res = self._update(req, conn=connection)
            if not res["OK"]:
                return res

        # We must also copy the run table entries if any
        result = self.getTransformationRuns({"TransformationID": originalID})
        if not result["OK"]:
            return result
        for runDict in res["Value"]:
            runID = runDict["RunNumber"]
            selectedSite = runDict["SelectedSite"]
            status = runDict["Status"]
            res = self.insertTransformationRun(
                transID, runID, selectedSite=selectedSite, status=status, connection=connection
            )
            if not res["OK"]:
                return res

        return S_OK()

    #############################################################################
    #
    # Managing the TransformationTasks table
    #

    def addTaskForTransformation(self, transID, lfns=[], se="Unknown", connection=False):
        """Create a new task with the supplied files for a transformation."""
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        connection = res["Value"]["Connection"]
        # Be sure the all the supplied LFNs are known to the database for the supplied transformation
        fileIDs = []
        runID = 0
        if lfns:
            res = self.getTransformationFiles(
                condDict={"TransformationID": transID, "LFN": lfns}, connection=connection
            )
            if not res["OK"]:
                return res
            foundLfns = set()
            for fileDict in res["Value"]:
                fileIDs.append(fileDict["FileID"])
                runID = fileDict.get("RunNumber")
                if not runID:
                    runID = 0
                lfn = fileDict["LFN"]
                if fileDict["Status"] in self.allowedStatusForTasks:
                    foundLfns.add(lfn)
                else:
                    gLogger.error(
                        f"Supplied file not in {self.allowedStatusForTasks} status but {fileDict['Status']}", lfn
                    )
            unavailableLfns = set(lfns) - foundLfns
            if unavailableLfns:
                return S_ERROR("Not all supplied files available in the transformation database")

        # Insert the task into the jobs table and retrieve the taskID
        self.lock.acquire()
        req = (
            "INSERT INTO TransformationTasks(TransformationID, ExternalStatus, ExternalID, \
    TargetSE, CreationTime, LastUpdateTime, RunNumber) VALUES\
     (%d,'%s','%d','%s', UTC_TIMESTAMP(), UTC_TIMESTAMP(),%d);"
            % (transID, "Created", 0, se, runID)
        )
        res = self._update(req, conn=connection)
        if not res["OK"]:
            self.lock.release()
            gLogger.error("Failed to publish task for transformation", res["Message"])
            return res

        # TaskID is computed by a trigger, which sets the local variable @last (per connection)
        # @last is the last insert TaskID. With multi-row inserts, will be the first new TaskID inserted.
        # The trigger TaskID_Generator must be present with the InnoDB schema (defined in TransformationDB.sql)
        res = self._query("SELECT @last;", conn=connection)

        self.lock.release()
        if not res["OK"]:
            return res
        taskID = int(res["Value"][0][0])
        gLogger.verbose("Published task %d for transformation %d." % (taskID, transID))
        # If we have input data then update their status, and taskID in the transformation table
        if lfns:
            res = self.__insertTaskInputs(transID, taskID, lfns, connection=connection)
            if not res["OK"]:
                self.__removeTransformationTask(transID, taskID, connection=connection)
                return res
            res = self.__assignTransformationFile(transID, taskID, se, fileIDs, connection=connection)
            if not res["OK"]:
                self.__removeTransformationTask(transID, taskID, connection=connection)
                return res
        return S_OK(taskID)

    #############################################################################
    #
    # Managing the TransformationRuns table
    #

    def getTransformationRuns(
        self,
        condDict=None,
        older=None,
        newer=None,
        timeStamp="LastUpdate",
        orderAttribute=None,
        limit=None,
        connection=False,
    ):
        """Gets the transformation runs registered (usual query)"""

        connection = self.__getConnection(connection)
        selectDict = {}
        if condDict:
            for key, val in condDict.items():
                if key in self.transRunParams:
                    selectDict[key] = val
        req = "SELECT {} FROM TransformationRuns {}".format(
            intListToString(self.transRunParams),
            self.buildCondition(
                selectDict, older=older, newer=newer, timeStamp=timeStamp, orderAttribute=orderAttribute, limit=limit
            ),
        )
        res = self._query(req, conn=connection)
        if not res["OK"]:
            return res
        webList = []
        resultList = []
        for row in res["Value"]:
            # Prepare the structure for the web
            rList = []
            transDict = {}
            for param, item in zip(self.transRunParams, row):
                transDict[param] = item
                rList.append(item if isinstance(item, int) else str(item))
            webList.append(rList)
            resultList.append(transDict)
        result = S_OK(resultList)
        result["Records"] = webList
        result["ParameterNames"] = copy.copy(self.transRunParams)
        return result

    def getTransformationRunStats(self, transIDs, connection=False):
        """Gets counters of runs (taken from the TransformationFiles table)"""
        connection = self.__getConnection(connection)
        res = self.getCounters(
            "TransformationFiles", ["TransformationID", "RunNumber", "Status"], {"TransformationID": transIDs}
        )
        if not res["OK"]:
            return res
        transRunStatusDict = {}
        for attrDict, count in res["Value"]:
            transID = attrDict["TransformationID"]
            runID = attrDict["RunNumber"]
            status = attrDict["Status"]
            transRunStatusDict[transID][runID]["Total"] = (
                transRunStatusDict.setdefault(transID, {}).setdefault(runID, {}).setdefault("Total", 0) + count
            )
            transRunStatusDict[transID][runID][status] = count
        return S_OK(transRunStatusDict)

    def addTransformationRunFiles(self, transID, runID, lfns, connection=False):
        """Adds the RunID to the TransformationFiles table."""
        if not lfns:
            return S_ERROR("Zero length LFN list")
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        lfnsDict = dict.fromkeys(lfns, {"RunNumber": runID})
        res = self.setParameterToTransformationFiles(transID, lfnsDict)
        if not res["OK"]:
            return res
        fileIDs = res["Value"]
        successful = dict.fromkeys(fileIDs.values(), "Added")
        failed = dict.fromkeys(set(lfns) - set(successful), "Missing")
        # Now update the TransformationRuns to include the newly updated files
        req = (
            "UPDATE TransformationRuns SET LastUpdate = UTC_TIMESTAMP() \
    WHERE TransformationID = %d and RunNumber = %d"
            % (transID, runID)
        )
        res = self._update(req, conn=connection)
        if not res["OK"]:
            gLogger.error("Failed to update TransformationRuns table with LastUpdate", res["Message"])
        elif not res["Value"]:
            self.insertTransformationRun(transID, runID, connection=connection)
        resDict = {"Successful": successful, "Failed": failed}
        return S_OK(resDict)

    def setParameterToTransformationFiles(self, transID, lfnsDict, connection=False):
        """Sets a parameter in the TransformationFiles table."""
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        connection = res["Value"]["Connection"]
        res = self.__getFileIDsForLfns(list(lfnsDict), connection=connection)
        if not res["OK"]:
            return res
        fileIDs = res["Value"][0]
        rDict = {fileID: lfnsDict[lfn] for fileID, lfn in fileIDs.items()}
        for fID, param in rDict.items():
            values = ",".join(f"`{k}` = NULL" if v is None else f"`{k}` = '{v}'" for k, v in param.items())
            query = "UPDATE TransformationFiles SET %s WHERE TransformationID = %d AND FileID = %d"
            query %= (values, transID, fID)
            res = self._update(query, conn=connection)
            if not res["OK"]:
                gLogger.error("Failed to update TransformationFiles table", res["Message"])
                return res
        return S_OK(fileIDs)

    def setTransformationRunStatus(self, transID, runIDs, status, connection=False):
        """Sets a status in the TransformationRuns table."""
        if not runIDs:
            return S_OK()
        if not isinstance(runIDs, list):
            runIDs = [runIDs]
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        connection = res["Value"]["Connection"]
        req = (
            "UPDATE TransformationRuns SET Status = '%s', LastUpdate = UTC_TIMESTAMP() \
    WHERE TransformationID = %d and RunNumber in (%s)"
            % (status, transID, intListToString(runIDs))
        )
        res = self._update(req, conn=connection)
        if not res["OK"]:
            gLogger.error("Failed to update TransformationRuns table with Status", res["Message"])
        return res

    def setTransformationRunsSite(self, transID, runID, selectedSite, connection=False):
        """Sets the site for Transformation Runs."""
        res = self._getConnectionTransID(connection, transID)
        if not res["OK"]:
            return res
        connection = res["Value"]["Connection"]
        req = (
            "UPDATE TransformationRuns SET SelectedSite = '%s', LastUpdate = UTC_TIMESTAMP() \
    WHERE TransformationID = %d and RunNumber = %d"
            % (selectedSite, transID, runID)
        )
        res = self._update(req, conn=connection)
        if not res["OK"]:
            gLogger.error("Failed to update TransformationRuns table with SelectedSite", res["Message"])
        elif not res["Value"]:
            res = self.insertTransformationRun(transID, runID, selectedSite=selectedSite, connection=connection)
        return res

    def insertTransformationRun(self, transID, runID, selectedSite="", status=None, connection=False):
        """Inserts a new Run for a specific transformation."""
        if status is None:
            status = "Active"
        if selectedSite:
            req = (
                "INSERT INTO TransformationRuns (TransformationID,RunNumber,SelectedSite,Status,LastUpdate) \
      VALUES (%d,%d,'%s','%s',UTC_TIMESTAMP())"
                % (transID, runID, selectedSite, status)
            )
        else:
            req = (
                "INSERT INTO TransformationRuns (TransformationID,RunNumber,Status,LastUpdate) \
      VALUES (%d,%d,'%s',UTC_TIMESTAMP())"
                % (transID, runID, status)
            )
        res = self._update(req, conn=connection)
        if not res["OK"]:
            gLogger.error("Failed to insert to TransformationRuns table", res["Message"])
        return res

    def __cleanTransformationRuns(self, transID, connection=False):
        req = f"DELETE  FROM TransformationRuns WHERE TransformationID = {transID}"
        res = self._update(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
        return res

    #############################################################################
    #
    # Managing the RunsMetadata table
    #

    def setRunsMetadata(self, runID, metadataDict, connection=False):
        """Add the metadataDict to runID (if already present, does nothing)"""
        connection = self.__getConnection(connection)
        for name, value in metadataDict.items():
            res = self.__insertRunMetadata(runID, name, value, connection)
            if not res["OK"]:
                return res
        return S_OK()

    def updateRunsMetadata(self, runID, metadataDict, connection=False):
        """Add the metadataDict to runID (if already present, does nothing)"""
        connection = self.__getConnection(connection)
        for name, value in metadataDict.items():
            res = self.__updateRunMetadata(runID, name, value, connection)
            if not res["OK"]:
                return res
        return S_OK()

    def __insertRunMetadata(self, runID, name, value, connection):
        if isinstance(runID, str):
            runID = int(runID)
        req = "INSERT INTO RunsMetadata (RunNumber, Name, Value) VALUES(%d, '%s', '%s')" % (runID, name, value)
        res = self._update(req, conn=connection)
        if not res["OK"]:
            if "1062: Duplicate entry" in res["Message"]:
                gLogger.debug(f"Failed to insert to RunsMetadata table: {res['Message']}")
                return S_OK()
            else:
                gLogger.error("Failed to insert to RunsMetadata table", res["Message"])
                return res
        gLogger.info("Inserted %s %s of run %d to RunsMetadata table" % (name, value, runID))
        return S_OK()

    def __updateRunMetadata(self, runID, name, value, connection):
        if isinstance(runID, str):
            runID = int(runID)
        req = "UPDATE RunsMetadata SET Value = %s WHERE RunNumber = %d AND Name = '%s'" % (value, runID, name)
        res = self._update(req, conn=connection)
        if not res["OK"]:
            gLogger.error("Failed to update RunsMetadata table", res["Message"])
            return res
        gLogger.info("Updated %s %s of run %d in RunsMetadata table" % (name, value, runID))
        return S_OK()

    def getRunsMetadata(self, runIDs, connection=False):
        """get meta of a run.

        RunIDs can be a list.
        """
        connection = self.__getConnection(connection)
        try:
            if isinstance(runIDs, (list, dict, set, tuple)):
                runIDs = ",".join(str(int(x)) for x in runIDs)
            else:
                runIDs = str(int(runIDs))
        except ValueError as e:
            gLogger.exception("Invalid run number", lException=e)
            return S_ERROR("Invalid run number")
        req = f"SELECT RunNumber, Name, Value FROM RunsMetadata WHERE RunNumber IN ({runIDs})"
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        else:
            dictOfNameValue = {}
            for runID, name, val in res["Value"]:
                dictOfNameValue.setdefault(runID, {}).update({name: val})
            return S_OK(dictOfNameValue)

    def deleteRunsMetadata(self, condDict=None, connection=False):
        """delete meta of a run.

        RunIDs can be a list.
        """
        connection = self.__getConnection(connection)
        req = f"DELETE FROM RunsMetadata {self.buildCondition(condDict)}"
        res = self._update(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        return S_OK()

    def getRunsInCache(self, condDict=None, connection=False):
        """get which runNumnber are cached."""
        connection = self.__getConnection(connection)
        req = f"SELECT DISTINCT RunNumber FROM RunsMetadata {self.buildCondition(condDict)}"
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        else:
            return S_OK([run[0] for run in res["Value"]])

    #############################################################################
    #
    # Managing the RunDestination table
    #

    def getDestinationForRun(self, runIDs, connection=False):
        """get destination of a run or a list of runs.
        This is to be deprecated by getAllDestinationForRuns
        but is here for backward compatibility
        """
        connection = self.__getConnection(connection)
        req = f"SELECT RunNumber,Destination FROM RunDestination WHERE RunNumber IN ({', '.join(str(runID) for runID in runIDs)})"
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        return S_OK(dict(res["Value"]) if res["Value"] else {})

    def getAllDestinationForRuns(self, runIDs, connection=False):
        """get destination and RAWDestination of a run or a list of runs."""
        connection = self.__getConnection(connection)
        req = f"""
        SELECT RunNumber, Destination, RAWDestination
        FROM RunDestination
        WHERE RunNumber IN ({', '.join(str(runID) for runID in runIDs)})
        """
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        if not res["Value"]:
            return S_OK({})

        return S_OK(
            {runNumber: [destination, rawDestination] for runNumber, destination, rawDestination in res["Value"]}
        )

    def setDestinationForRun(self, runID, *, destination="", rawDestination="", connection=False):
        """set destination of a run."""
        connection = self.__getConnection(connection)
        # We always start by inserting the RAWDestination
        # In case we have both, it is for manual insertion
        if rawDestination:
            req = f"""
            INSERT INTO RunDestination (RunNumber, Destination, RAWDestination)
            VALUES ({runID}, '{destination}', '{rawDestination}')
            """
            return self._query(req, conn=connection)
        elif destination:
            # We always set the destination after the RAWDestination, so it can be a simple update
            # Also we add the constraint that it isn't set yet
            req = f"""Update RunDestination
            SET Destination = '{destination}'
            WHERE RunNumber = {runID} AND Destination = ''
            """
            res = self._update(req, conn=connection)
            if not res["OK"]:
                return res

            if not res["Value"]:
                return S_ERROR("Destination already set or run not existing !")

            return res
        else:
            return S_ERROR("At least one of destination or rawDestination must be set")

    #############################################################################
    #
    # Managing the StoredJobDescription table
    #

    def addStoredJobDescription(self, transformationID, jobDescription, connection=False):
        """store a job description for transformationID."""
        connection = self.__getConnection(connection)
        res = self._escapeString(jobDescription)
        if not res["OK"]:
            return S_ERROR("Failed to parse the transformation body")
        jobDescription = res["Value"]
        req = "INSERT INTO StoredJobDescription (TransformationID, JobDescription) VALUES (%d, %s)" % (
            transformationID,
            jobDescription,
        )
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        else:
            return S_OK()

    def getStoredJobDescription(self, transformationID, connection=False):
        """get the job description for transformationID."""
        connection = self.__getConnection(connection)
        req = "SELECT * FROM StoredJobDescription WHERE TransformationID = %d" % transformationID
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        else:
            return S_OK(res["Value"])

    def removeStoredJobDescription(self, transformationID, connection=False):
        """remove the job description for transformationID."""
        connection = self.__getConnection(connection)
        req = "DELETE FROM StoredJobDescription WHERE TransformationID = %d" % transformationID
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        else:
            return S_OK()

    def getStoredJobDescriptionIDs(self, connection=False):
        """gets a list of all the stored job description transformationIDs."""
        connection = self.__getConnection(connection)
        req = "SELECT TransformationID FROM StoredJobDescription"
        res = self._query(req, conn=connection)
        if not res["OK"]:
            gLogger.error(f"Failure executing {str(req)}")
            return res
        else:
            return S_OK(res["Value"])

    def compareTasksAndInputLFNs(self, parentID, childID, connection=False):
        """Compare tasks and input LFNs with the tasks of the parent transformation.

        In the ProductionStatusAgent, there is a potential race condition where
        the child transformation is completed before all of the input LFNs are
        added by the BookkeepingWatchAgent.

        Additionally, the task status of the parent transformation can be
        inconsistent with the file status due to jobs failing after files have
        been marked as Processed.

        This function uses the LHCb convention for LFNs to extract the task ID
        from the LFN and return consistency information between the parents
        tasks and the child's input.
        """
        req = f"""WITH TasksFromInputLFNs AS (
    SELECT DISTINCT
        CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(LFN, '/', -1), '_', 2), '_', -1) AS UNSIGNED) as file_number
    FROM DataFiles
    WHERE FileID IN (SELECT FileID FROM TransformationFiles WHERE TransformationID = {childID:0d})
)
SELECT DISTINCT tt.TaskID, tt.ExternalStatus, tt.ExternalID,
       CASE WHEN tfi.file_number IS NOT NULL THEN TRUE ELSE FALSE END as HasInputFile
FROM TransformationFiles tf
LEFT JOIN TransformationTasks tt ON tt.TaskID = tf.TaskID AND tf.TransformationID = tt.TransformationID
LEFT OUTER JOIN TasksFromInputLFNs tfi ON tfi.file_number = tf.TaskID
WHERE tf.TransformationID = {parentID:0d} AND tf.Status = 'Processed'"""
        res = self._query(req, conn=connection)
        if not res["OK"]:
            return res
        result = []
        for row in res["Value"]:
            result.append(
                {
                    "TaskID": row[0],
                    "ExternalStatus": row[1],
                    "ExternalID": row[2],
                    "HasInputFile": bool(row[3]),
                }
            )
        return S_OK(result)

    def getOpsOverview(self, category, connection=False):
        """Get a summary of the transformations for the Analysis Production Operations dashboard.

        There are four valid categories:
            - "AP": Analysis Production transformations
            - "MC": Monte Carlo production transformations
            - "DM": Data Management transformations
            - "Other": Transformations not in the above categories
        """
        connection = self.__getConnection(connection)

        match category:
            case category if category in AP_OPS_TYPE_MAPPING:
                types = AP_OPS_TYPE_MAPPING[category]
                types_op = "IN"
            case "Other":
                types = sorted({t for ts in AP_OPS_TYPE_MAPPING.values() for t in ts})
                types_op = "NOT IN"
            case _:
                raise NotImplementedError(f"Unrecognised category {category}")
        type_query = f"Type {types_op} ({', '.join(map(repr, types))})"

        res = self._query(AP_OPS_QUERY.format(type_query=type_query), conn=connection)
        if not res["OK"]:
            gLogger.error("Failure executing AP Ops overview query", res["Message"])
            return res
        keys = [col.split(".", 1)[-1] for col in AP_OPS_COLUMNS]
        result = [dict(zip(keys, row)) for row in res["Value"]]
        for row in result:
            row["FileStatusCounts"] = json.loads(row["FileStatusCounts"] or "{}")
            row["TaskStatusCounts"] = json.loads(row["TaskStatusCounts"] or "{}")
            if row["InputBKQuery"]:
                row["InputBKQuery"] = {
                    k: json.loads(v) if v.startswith("[") else v for k, v in json.loads(row["InputBKQuery"]).items()
                }
        return S_OK(result)


AP_OPS_TYPE_MAPPING = {
    "AP": ["APPostProc", "APMerge", "WGProduction"],
    "MC": ["MCSimulation", "MCFastSimulation", "MCReconstruction", "MCMerge"],
    "DM": ["Replication", "Removal"],
}
AP_OPS_COLUMNS = [
    "t.TransformationID",
    "t.TransformationFamily",
    "t.Type",
    "t.Status",
    "t.TransformationName",
    "t.Plugin",
    "t.GroupSize",
    "t.CreationDate",
    "tfs.FileStatusCounts",
    "tts.TaskStatusCounts",
    "tiq.InputBKQuery",
]

AP_OPS_QUERY = f"""
WITH ActiveTransformations AS (
    select
        TransformationID,
        TransformationFamily,
        Type,
        Status,
        TransformationName,
        Plugin,
        GroupSize,
        CreationDate
    from Transformations
    where {{type_query}} and Status in ('Idle', 'Active', 'Flush')
),
TransformationFileStatus AS (
    SELECT TransformationID, Status, COUNT(*) AS FileCount
    FROM TransformationFiles
    WHERE TransformationID IN (SELECT TransformationID FROM ActiveTransformations)
    GROUP BY TransformationID, Status
),
TransformationFileStatusAgg AS (
    SELECT TransformationID, JSON_OBJECTAGG(Status, FileCount) as FileStatusCounts
    FROM TransformationFileStatus
    GROUP BY TransformationID
),
TransformationInputQueries AS (
    SELECT
        TransformationID,
        JSON_OBJECTAGG(
            ParameterName,
            CASE
                WHEN ParameterValue LIKE '%;;;%' THEN
                    CAST(CONCAT('["', REPLACE(ParameterValue, ';;;', '","'), '"]') AS JSON)
                ELSE ParameterValue
            END
        ) as InputBKQuery
    FROM `BkQueriesNew`
    WHERE
        TransformationID in (SELECT TransformationID FROM ActiveTransformations)
        AND ParameterValue != 'All'
        AND NOT (ParameterName IN ('StartRun', 'EndRun') AND ParameterValue = '0')
    GROUP BY TransformationID
),
TransformationTaskStatus AS (
    SELECT TransformationID, ExternalStatus AS Status, COUNT(DISTINCT TaskID) AS TaskCount
    FROM TransformationTasks
    INNER JOIN TransformationFiles USING (TransformationID, TaskID)
    WHERE TransformationID IN (SELECT TransformationID FROM ActiveTransformations)
    AND TransformationFiles.Status != 'Unused'
    GROUP BY TransformationID, ExternalStatus
),
TransformationTaskStatusAgg AS (
    SELECT TransformationID, JSON_OBJECTAGG(Status, TaskCount) as TaskStatusCounts
    FROM TransformationTaskStatus
    GROUP BY TransformationID
)
select
    {', '.join(AP_OPS_COLUMNS)}
from ActiveTransformations t
left outer join TransformationFileStatusAgg tfs using (TransformationID)
left outer join TransformationTaskStatusAgg tts using (TransformationID)
left outer join TransformationInputQueries tiq using (TransformationID)
"""
