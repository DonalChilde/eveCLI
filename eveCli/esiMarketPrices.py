import asyncQueueRunner.asyncHttpQueueRunner as AQR
import argparse
import sys
from datetime import datetime

API_NAME = "EVE Market Prices"
EVE_ESI = "https://esi.evetech.net/latest/"
API = "markets/prices/"
FILENAME = "MarketPrices"
DATETIMESTRING = datetime.utcnow().strftime('%Y-%m-%dT%H.%M.%S')

# TODO implement default name, with datetime prefix?


class EsiMarketPrices(object):
    def __init__(self):
        pass

    def buildRequest(self, callback=None, internalParams: dict = None) -> AQR.AsyncHttpRequest:
        url = EVE_ESI+API
        requestParams = {'params': {'datasource': 'tranquility'}}
        request = AQR.AsyncHttpRequest.get(
            url, requestParams=requestParams, storeResults=True,callback=callback,internalParams=internalParams)
        return request

    def getData(self, request: AQR.AsyncHttpRequest) -> str:
        queueRunner = AQR.AsyncHttpQueueRunner()
        queueRunner.execute((request,), 1)
        data = request.completedActionData
        return data

    def formatData(self, data, outputFormat):
        if outputFormat == 'json':
            return data
        if outputFormat == 'csv':
            csvData = self.convertToCsv(data)
            return csvData
        if outputFormat == 'both':
            csvData = self.convertToCsv(data)
            dataTuple = (data, csvData)
            return dataTuple

    def convertToCsv(self, data):
        raise NotImplementedError


class MarketPricesCmdLineParser(object):
    def __init__(self, cmdLineArgs):
        self.cmdLineArgs = cmdLineArgs
        self.target = EsiMarketPrices()

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
        parser = self.defineCmdParser()
        parsedCommands = parser.parse_args(self.cmdLineArgs[1:])
        self.validateCommands(parsedCommands, parser)
        request = self.target.buildRequest()
        data = self.target.getData(request)
        formattedData = self.target.formatData(
            data, parsedCommands.outputFormat)
        if parsedCommands.outputFolderPath == 'stdout':
            self.printToStdOut(formattedData)

    def validateCommands(self, parsedCommands, parser):
        pass

    def printToStdOut(self, formattedData):
        print(formattedData)

    def getFilename(self):
        pass


# def check_arg(args=None):
#     parser = argparse.ArgumentParser(
#         description=f'Script to download {API_NAME} from {EVE_ESI+API}')
#     parser.add_argument('-p', '--outputFolderPath',
#                         help='Optional. Output folder path, ie. </foo/bar/> .  If not given, will output to stdout.')
#     parser.add_argument('-n', '--outputFileName',
#                         help=f'Optional. Output file name, with no file type ending. ie. <foo> not <foo.json>. If not given, \
#                         the default filename of {FILENAME}_{DATETIMESTRING}.<format> will be used.')
#     parser.add_argument('-f', '--outputFormat',
#                         help='Default = json. Output format. Supported formats are, json, csv, or both.',
#                         default='json',
#                         choices=['json', 'csv', 'both'])
#     # parser.add_argument('-u', '--user',
#     #                     help='user name',
#     #                     default='root')

#     results = parser.parse_args(args)
#     return results


if __name__ == '__main__':
    cmdParser = MarketPricesCmdLineParser(sys.argv)
    cmdParser.doCmdLine()
    # results = check_arg()
    # outputFolderPath = results.outputFolderPath
    # outputFileName = results.outputFileName
    # outputFormat = results.outputFormat
    # print(f'p = {outputFolderPath}')
    # print(f'n = {outputFileName}')
    # print(f'f = {outputFormat}')
    # print(f'date string {DATETIMESTRING}')
    # data = getData()
    # formattedData = formatData(data, outputFormat)
    # if outputFolderPath == None:
    #     print(data)
