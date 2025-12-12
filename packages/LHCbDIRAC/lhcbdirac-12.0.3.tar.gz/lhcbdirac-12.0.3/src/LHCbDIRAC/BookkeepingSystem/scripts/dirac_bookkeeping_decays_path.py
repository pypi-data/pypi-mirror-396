#!/usr/bin/env python
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
"""Get Bookkeeping paths given a decay."""
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.Core.Utilities.ReturnValues import convertToReturnValue

IGNORED_FILETYPES = ["GAUSSHIST", "LOG", "SIM", "DIGI", "RAW", "GAUSSHISTMERGED"]


def parseArgs():
    productionFormat = False
    configName = None
    configVersion = None
    onlyBKPaths = False

    @convertToReturnValue
    def setProductionFormat(_):
        nonlocal productionFormat
        productionFormat = True

    @convertToReturnValue
    def setConfigName(s: str):
        nonlocal configName
        configName = s

    @convertToReturnValue
    def setConfigVersion(s: str):
        nonlocal configVersion
        configVersion = s

    @convertToReturnValue
    def setOnlyBKPaths(_):
        nonlocal onlyBKPaths
        onlyBKPaths = True

    switches = [
        ("p", "production", "Obtain the paths in ``Production format'' for Ganga", setProductionFormat),
        ("", "config-name=", "Filter by configuration name", setConfigName),
        ("", "config-version=", "Filter by configuration version", setConfigVersion),
        ("", "only-bk-paths", "Only return the paths, not the production information", setOnlyBKPaths),
    ]
    Script.registerSwitches(switches)
    Script.registerArgument("eventType: Event type to search for")
    Script.parseCommandLine(ignoreErrors=False)

    eventType = Script.getPositionalArgs(group=True)

    return eventType, productionFormat, configName, configVersion, onlyBKPaths


@Script()
def main():
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    eventType, productionFormat, configName, configVersion, onlyBKPaths = parseArgs()

    bkClient = BookkeepingClient()

    # # get productions for given event type
    query = {"EventType": eventType, "Visible": True}
    if configName is not None:
        query["ConfigName"] = configName
    if configVersion is not None:
        query["ConfigVersion"] = configVersion
    res = bkClient.listBookkeepingPaths(query)
    if not res["OK"]:
        gLogger.error(f"Could not retrieve production summary for event {eventType}", res["Message"])
        DIRAC.exit(1)

    if onlyBKPaths:
        for bkdict in res["Value"]:
            bk_path_parts = [
                bkdict["ConfigName"],
                bkdict["ConfigVersion"],
                bkdict["ConditionDescription"],
                bkdict["ProcessingPass"].strip("/"),
                str(bkdict["EventType"]),
                bkdict["FileType"],
            ]
            print("/" + "/".join(bk_path_parts))
        return

    # # get production-IDs
    prodIDs = sorted({p["Production"] for p in res["Value"]})

    # # loop over all productions
    for prodID in sorted(prodIDs):
        res = bkClient.getProductionInformation(prodID)
        if not res["OK"]:
            gLogger.error(f"Could not retrieve production infos for production {prodID}", res["Message"])
            continue
        prodInfo = res["Value"]
        steps = prodInfo["Steps"]
        if isinstance(steps, str):
            continue
        files = prodInfo["Number of files"]
        events = prodInfo["Number of events"]
        path = prodInfo["Path"]
        dddb = prodInfo["Steps"][0][4]
        conddb = prodInfo["Steps"][0][5]

        evts = 0
        ftype = None
        for i in events:
            if i[0] in IGNORED_FILETYPES:
                continue
            # NB of events can sometimes be None
            if i[1] is not None:
                evts += i[1]

            if not ftype:
                ftype = i[0]

        nfiles = 0
        for f in files:
            if f[1] in IGNORED_FILETYPES:
                continue
            if f[1] != ftype:
                continue
            nfiles += f[0]

        p0, n, p1 = path.partition("\n")
        if n:
            path = p1

        if productionFormat:
            p, s, e = path.rpartition("/")
            if s and e:
                path = "/%d/%d/%s" % (prodID, int(eventType), e)
        print(path, dddb, conddb, nfiles, evts, prodID)


if __name__ == "__main__":
    main()
