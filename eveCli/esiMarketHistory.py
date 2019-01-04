
import asyncQueueRunner.asyncHttpQueueRunner as AQR
import argparse
import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List
from localUtils import saveToFile


# setting up logger
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# console = logging.StreamHandler()
# logger.addHandler(console)

API_NAME = "EVE Market History"
EVE_ESI = "https://esi.evetech.net/latest/"
API = "markets/<region_id>/history/?datasource=tranquility&type_id=<type_id>"
FILENAME = "MarketHistory_<region_id>_<type_id>_"
DATETIMESTRING = datetime.utcnow().strftime('%Y-%m-%dT%H.%M.%S')
MAX_CONNECTIONS = 100

# Done - implement default name, with datetime prefix?
# TODO figure out headers, useragent etc
# TODO add code for csv format
# Done - add code for saving files
# Done - add code for loading region and type from file
# TODO - implement wrapper json, to allow saving of request parameters and date
# TODO - more validation checks for inputs, re job loading
# TODO - option to print time to completion, and other stats.


class EsiMarketHistory(object):
    def __init__(self):
        pass

    def convertToCsv(self, data):
        raise NotImplementedError()

    def buildRequest(self, region_id: int, type_id: int, storeResults=True, callback=None, internalParams: dict = None) -> AQR.AsyncHttpRequest:
        api = f"markets/{region_id}/history/"
        url = EVE_ESI+api
        requestParams = {'params': {
            'datasource': 'tranquility', 'type_id': type_id}}
        request = AQR.AsyncHttpRequest.get(
            url, requestParams=requestParams, storeResults=storeResults, callback=callback, internalParams=internalParams)
        return request

    def getRequests(self, requests: List[AQR.AsyncHttpRequest], sessionParams: dict = None):
        if len(requests) <= MAX_CONNECTIONS:
            connections = len(requests)
        else:
            connections = MAX_CONNECTIONS
        queueRunner = AQR.AsyncHttpQueueRunner()
        queueRunner.execute(requests, connections, sessionParams=sessionParams)
        # return requests

    def getData(self, request: AQR.AsyncHttpRequest) -> str:
        # self.getRequests((request,))
        data = request.completedActionData
        return data

    def formatData(self, data, outputFormat):
        logger.debug(data)
        if outputFormat == 'json':
            return ((self.formatJson(data), 'json'),)
        if outputFormat == 'csv':
            return ((self.formatCsv(data), 'csv'),)
        if outputFormat == 'both':
            return ((self.formatJson(data), 'json'), (self.formatCsv(data), 'csv'))

    def formatJson(self, data):
        return data

    def formatCsv(self, data):
        csvData = self.convertToCsv(data)
        return csvData

    # def getSingleResult(self, parsedCommands):
    #     region_id, type_id = parsedCommands.regionid_typeid
    #     outputFileName = parsedCommands.outputFileName
    #     outputPath = parsedCommands.outputPath
    #     outputFormat = parsedCommands.outputFormat
    #     request = self.buildRequest(region_id,type_id)
    #     data = self.getData(request)
    #     formattedData = self.formatData(data, outputFormat)
    #     return formattedData


class MarketHistoryCmdLineParser(object):
    def __init__(self, cmdArgs):
        self.cmdArgs = cmdArgs
        self.target = EsiMarketHistory()
        self.parser = self.defineCmdParser()

    def defineCmdParser(self):
        parser = argparse.ArgumentParser(
            description=f'Script to download {API_NAME} from {EVE_ESI+API}')
        subparsers = parser.add_subparsers(
            help="Available Commands", dest='command')
        getMany = subparsers.add_parser('getmany', help='many help')
        getMany.add_argument('jsonInstructions',
                             help='Path to json file with a list of region_id and type_id pairs.')
        getMany.add_argument('-p', '--outputFolderPath', default='stdout',
                             help='Default = stdout. Output folder path, ie. </foo/bar/>.')
        getMany.add_argument('-f', '--outputFormat',
                             help='Default = json. Output format. Supported formats are, json, csv, or both.',
                             default='json',
                             choices=['json', 'csv', 'both'])

        getOne = subparsers.add_parser('getone')
        getOne.add_argument('regionid_typeid', nargs=2, type=int,
                            help='region_id and type_id, ie. 10000002 34')
        getOne.add_argument('-n', '--outputFileName',
                            help=f'Default = {FILENAME}_{DATETIMESTRING}.<format>.\
                            Output file name, with no file type ending. ie. <foo> not <foo.json>.')
        getOne.add_argument('-p', '--outputFolderPath', default='stdout',
                            help='Default = stdout. Output folder path, ie. </foo/bar/>.')
        getOne.add_argument('-f', '--outputFormat',
                            help='Default = json. Output format. Supported formats are, json, csv, or both.',
                            default='json',
                            choices=['json', 'csv', 'both'])
        return parser

    def doCmdLine(self):
        # parser = self.defineCmdParser()
        parsedCommands = self.parser.parse_args(self.cmdArgs[1:])
        self.validateCommands(parsedCommands)
        if parsedCommands.command == 'getone':
            if parsedCommands.outputFolderPath == 'stdout':
                self.printToStdOut(parsedCommands)
            else:
                self.saveToFile(parsedCommands)
        if parsedCommands.command == 'getmany':
            if parsedCommands.outputFolderPath == 'stdout':
                self.printToStdOut(parsedCommands)
            else:
                self.saveToFile(parsedCommands)

    def validateCompletedRequest(self, request):
        pass

    def printToStdOut(self, parsedCommands):
        if parsedCommands.command == 'getone':
            region_id, type_id = parsedCommands.regionid_typeid
            request = self.target.buildRequest(region_id, type_id)
            self.target.getRequests((request,))
            self.validateCompletedRequest(request)
            data = self.target.getData(request)
            formattedData = self.target.formatData(
                data, parsedCommands.outputFormat)
            for item in formattedData:
                print(item[0])
        if parsedCommands.command == 'getmany':
            raise NotImplementedError()

    def validateCommands(self, parsedCommands):
        if parsedCommands.command == 'getmany':
            if not Path(parsedCommands.jsonInstructions).exists():
                self.parser.error(
                    f"{parsedCommands.jsonInstructions} does not exist. Please provide a valid path.")
            if not parsedCommands.outputFolderPath == 'stdout':
                if not Path(parsedCommands.outputFolderPath).is_dir():
                    self.parser.error(
                        f"{parsedCommands.outputFolderPath} does not exist or is not a folder/directory. \
                        Please provide a valid path.")
        if parsedCommands.command == 'getone':
            if not parsedCommands.outputFolderPath == 'stdout':
                if not Path(parsedCommands.outputFolderPath).is_dir():
                    self.parser.error(
                        f"{parsedCommands.outputFolderPath} does not exist or is not a folder/directory. \
                        Please provide a valid path.")

    # def printToStdOut(self, formattedData):
    #     print(formattedData)

    #     # print(argResults)

    def getFilename(self, region_id, type_id):
        filenameTemplate = f"MarketHistory_{region_id}_{type_id}_"
        # dateString = datetime.utcnow().strftime('%Y-%m-%dT%H.%M.%S')
        return filenameTemplate + DATETIMESTRING

    def getJobsFromFile(self, parsedCommands):
        jobPath = parsedCommands.jsonInstructions
        jobs = None
        with open (jobPath,'r') as jobFile:
            jobs=json.load(jobFile)
        return jobs

    def saveToFile(self, parsedCommands):
        if parsedCommands.command == 'getone':
            path = parsedCommands.outputFolderPath
            region_id, type_id = parsedCommands.regionid_typeid
            if parsedCommands.outputFileName:
                filename = parsedCommands.outputFileName
            else:
                filename = self.getFilename(region_id, type_id)
            internalParams = {'filename': filename, 'path': path,
                              'formatter': self.target, 'format': parsedCommands.outputFormat}
            callback = saveMarketHistory
            request = self.target.buildRequest(
                region_id=region_id, type_id=type_id, internalParams=internalParams, callback=callback)
            self.target.getRequests((request,))
        if parsedCommands.command == 'getmany':
            jobs = self.getJobsFromFile(parsedCommands)
            requests = []
            for item in jobs:
                path = parsedCommands.outputFolderPath
                # TODO move this to a function for data check
                region_id, type_id = item['region_id'], item['type_id']
                filename = self.getFilename(region_id, type_id)
                internalParams = {'filename': filename, 'path': path,
                                  'formatter': self.target, 'format': parsedCommands.outputFormat}
                callback = saveMarketHistory
                request = self.target.buildRequest(
                    region_id=region_id, type_id=type_id, internalParams=internalParams, callback=callback)
                requests.append(request)
            self.target.getRequests(requests)


async def saveMarketHistory(state: AQR.RequestState) -> AQR.RequestState:
    outputFormat = state.action.internalParams['format']
    path = state.action.internalParams['path']
    filenameRoot = state.action.internalParams['filename']
    formattedData = state.action.internalParams['formatter'].formatData(
        state.responseText, outputFormat)
    for item in formattedData:
        filename = filenameRoot + '.'+item[1]
        saveToFile(path, filename, item[0])
    return state


if __name__ == '__main__':
    cmdParser = MarketHistoryCmdLineParser(sys.argv)
    cmdParser.doCmdLine()

    # print(results)
    # if argResults.command == 'getone':
    #     getSingleResult(argResults)
    # jsonInstructions = results.jsonInstructions
    # outputPath = results.outputPath
    # outputFileName = results.outputFileName
    # outputFormat = results.outputFormat
    # region_id = results.region_id
    # type_id = results.type_id
    # print(f'p = {outputPath}')
    # print(f'n = {outputFileName}')
    # print(f'f = {outputFormat}')
    # print(f'r = {region_id}')
    # print(f't = {type_id}')
    # print(f'date string {DATETIMESTRING}')
    # data = getData()
    # formattedData = formatData(data, outputFormat)
    # if outputPath == None:
    #     print(data)
