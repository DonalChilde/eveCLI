import asyncQueueRunner.asyncHttpQueueRunner as AQR
import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List
from utils import saveToFile


# setting up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# console = logging.StreamHandler()
# logger.addHandler(console)
API_NAME = "EVE Market Prices"
EVE_ESI = "https://esi.evetech.net/latest/"
API = "markets/prices/"
FILENAME = "MarketPrices"
DATETIMESTRING = datetime.utcnow().strftime('%Y-%m-%dT%H.%M.%S')
MAX_CONNECTIONS = 100

# DONE - implement default name, with datetime prefix?
# TODO - implement wrapper json, to allow saving of request parameters and date


class EsiMarketPrices(object):
    def __init__(self):
        pass

    def buildRequest(self, storeResults=True, callback=None, internalParams: dict = None) -> AQR.AsyncHttpRequest:
        url = EVE_ESI+API
        requestParams = {'params': {'datasource': 'tranquility'}}
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
        # self.getOneRequest(request)
        # self.getRequests((request,))
        data = request.completedActionData
        return data

    def formatData(self, data, outputFormat):
        if outputFormat == 'json':
            return ((self.formatJson(data),'json'),)
        if outputFormat == 'csv':
            return ((self.formatCsv(data),'csv'),)
        if outputFormat == 'both':
            return ((self.formatJson(data), 'json'), (self.formatCsv(data), 'csv'))

    def formatJson(self, data):
        return data

    def formatCsv(self, data):
        csvData = self.convertToCsv(data)
        return csvData
    def convertToCsv(self, data):
        raise NotImplementedError


class MarketPricesCmdLineParser(object):
    def __init__(self, cmdLineArgs):
        self.cmdLineArgs = cmdLineArgs
        self.target = EsiMarketPrices()
        self.parser = self.defineCmdParser()

    def defineCmdParser(self):
        parser = argparse.ArgumentParser(
            description=f'Script to download {API_NAME} from {EVE_ESI+API}')
        parser.add_argument('-p', '--outputFolderPath', default='stdout',
                            help='Optional. Output folder path, ie. </foo/bar/> .  If not given, will output to stdout.')
        parser.add_argument('-n', '--outputFileName',
                            help=f'Optional. Output file name, with no file type ending. ie. <foo> not <foo.json>. If not given, \
                            the default filename of {FILENAME}_{DATETIMESTRING}.<format> will be used.')
        parser.add_argument('-f', '--outputFormat',
                            help='Default = json. Output format. Supported formats are, json, csv, or both.',
                            default='json',
                            choices=['json', 'csv', 'both'])
        return parser

    def doCmdLine(self):
        # parser = self.defineCmdParser()
        parsedCommands = self.parser.parse_args(self.cmdLineArgs[1:])
        self.validateCommands(parsedCommands)
        if parsedCommands.outputFolderPath == 'stdout':
            self.printToStdOut(parsedCommands.outputFormat)
        else:
            self.saveToFile(parsedCommands)

    def validateCommands(self, parsedCommands):
        # check path valid
        # check filename valid
        pass

    def validateCompletedRequest(self, request):
        pass

    def printToStdOut(self, outputFormat):
        request = self.target.buildRequest()
        self.target.getRequests((request,))
        self.validateCompletedRequest(request)
        data = self.target.getData(request)
        formattedData = self.target.formatData(
            data, outputFormat)
        for item in formattedData:
            print(item[0])
        # print(formattedData[0])

    def saveToFile(self, parsedCommands):
        # print('saveToFile')
        path = parsedCommands.outputFolderPath
        if parsedCommands.outputFileName:
            filename = parsedCommands.outputFileName
        else:
            filename = f"{FILENAME}_{DATETIMESTRING}"
        internalParams = {'filename':filename,'path':path,'formatter':self.target,'format':parsedCommands.outputFormat}
        callback=saveMarketPrice
        request = self.target.buildRequest(internalParams=internalParams,callback=callback)
        self.target.getRequests((request,))
        

        # callback = AQR.saveFileCallback
        pass

async def saveMarketPrice(state: AQR.RequestState) -> AQR.RequestState:
    # print('made it to callback')
    outputFormat = state.action.internalParams['format']
    path = state.action.internalParams['path']
    filenameRoot = state.action.internalParams['filename']
    formattedData = state.action.internalParams['formatter'].formatData(state.responseText,outputFormat)
    # print(state.action.response.status)
    # print(formattedData)
    for item in formattedData:
        # print(item[0])
        filename = filenameRoot + '.'+item[1]
        saveToFile(path,filename,item[0])
    return state




if __name__ == '__main__':
    cmdParser = MarketPricesCmdLineParser(sys.argv)
    cmdParser.doCmdLine()
