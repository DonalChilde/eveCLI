
import asyncQueueRunner.asyncHttpQueueRunner as AQR
import argparse
import sys
from pathlib import Path
from datetime import datetime

API_NAME = "EVE Market History"
EVE_ESI = "https://esi.evetech.net/latest/"
API = "markets/<region_id>/history/?datasource=tranquility&type_id=<type_id>"
FILENAME = "MarketHistory_<region_id>_<type_id>_"
DATETIMESTRING = datetime.utcnow().strftime('%Y-%m-%dT%H.%M.%S')

# TODO implement default name, with datetime prefix?
# TODO figure out headers, useragent etc


def check_arg(args=None):
    parser = argparse.ArgumentParser(
        description=f'Script to download {API_NAME} from {EVE_ESI+API}')
    subparsers = parser.add_subparsers(
        help="Available Commands", dest='command')
    getMany = subparsers.add_parser('getmany', help='many help')
    getMany.add_argument('jsonInstructions',
                         help='Path to json file with a list of region_id and type_id pairs.')
    getMany.add_argument('-o', '--outputPath', default='stdout',
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
    getOne.add_argument('-o', '--outputPath', default='stdout',
                        help='Default = stdout. Output folder path, ie. </foo/bar/>.')
    getOne.add_argument('-f', '--outputFormat',
                        help='Default = json. Output format. Supported formats are, json, csv, or both.',
                        default='json',
                        choices=['json', 'csv', 'both'])
    # inputGroup.add_argument('-i', '--jsonInstructions',
    #                         help='Get region_id and type_id from file')

    # parser.add_argument('-u', '--user',
    #                     help='user name',
    #                     default='root')

    results = parser.parse_args(args)
    print(results)
    validateCommands(results, parser)
    return results


def validateCommands(results, parser):
    if results.command == 'getmany':
        if not Path(results.jsonInstructions).exists():
            parser.error(
                f"{results.jsonInstructions} does not exist. Please provide a valid path.")
        if not results.outputPath == 'stdout':
            if not Path(results.outputPath).exists() or not Path(results.outputPath).is_dir():
                parser.error(
                    f"{results.outputPath} does not exist or is not a folder/directory. \
                    Please provide a valid path.")
    if results.command == 'getone':
        if not results.outputPath == 'stdout':
            if not Path(results.outputPath).exists() or not Path(results.outputPath).is_dir():
                parser.error(
                    f"{results.outputPath} does not exist or is not a folder/directory. \
                    Please provide a valid path.")


def getData(region_id, type_id) -> str:
    responseHandler = AQR.AsyncHttpGetResponseHandler(storeResults=True)
    api = f"markets/{region_id}/history/?datasource=tranquility&type_id={type_id}"
    url = EVE_ESI+api
    action = AQR.AsyncHttpGet(url, responseHandler=responseHandler)
    queueRunner = AQR.AsyncHttpQueueRunner()
    queueRunner.execute((action,), 1)
    data = action.completedActionData
    return data


def formatData(data, outputFormat):
    if outputFormat == 'json':
        return data
    if outputFormat == 'csv':
        csvData = convertToCsv(data)
        return csvData
    if outputFormat == 'both':
        csvData = convertToCsv(data)
        dataTuple = (data, csvData)
        return dataTuple


def convertToCsv(data):
    return "Not Implemeted"


def printToStdOut(formattedData):
    print(formattedData)


def getSingleResult(argResults):
    region_id, type_id = argResults.regionid_typeid
    outputFileName = argResults.outputFileName
    outputPath = argResults.outputPath
    outputFormat = argResults.outputFormat
    data = getData(region_id, type_id)
    formattedData = formatData(data, outputFormat)
    if outputPath == 'stdout':
        printToStdOut(formattedData)
    # print(argResults)


def getFilename(region_id, type_id):
    filenameTemplate = f"MarketHistory_{region_id}_{type_id}_"
    dateString = datetime.utcnow().strftime('%Y-%m-%dT%H.%M.%S')
    return filenameTemplate + dateString


def saveToFile(formattedData, path, filename):
    pass


if __name__ == '__main__':
    argResults = check_arg()

    # print(results)
    if argResults.command == 'getone':
        getSingleResult(argResults)
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
