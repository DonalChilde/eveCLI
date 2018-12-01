
import asyncQueueRunner.asyncHttpQueueRunner as AQR
import argparse
import sys
from datetime import datetime

API_NAME = "EVE Market History"
EVE_ESI = "https://esi.evetech.net/latest/"
API = "markets/<region_id>/history/?datasource=tranquility&type_id=<type_id>"
FILENAME = "MarketHistory_region_id-<region_id>_type_id-<type_id>"
DATETIMESTRING = datetime.utcnow().strftime('%Y-%m-%dT%H.%M.%S')

# TODO implement default name, with datetime prefix?


def check_arg(args=None):
    parser = argparse.ArgumentParser(
        description=f'Script to download {API_NAME} from {EVE_ESI+API}')
    parser.add_argument('-p', '--outputFolderPath',
                        help='Optional. Output folder path, ie. </foo/bar/> .  If not given, will output to stdout.')
    parser.add_argument('-n', '--outputFileName',
                        help=f'Optional. Output file name, with no file type ending. ie. <foo> not <foo.json>. If not given, \
                        the default filename of {FILENAME}_{DATETIMESTRING}.<format> will be used.')
    parser.add_argument('-f', '--outputFormat',
                        help='Default = json. Output format. Supported formats are, json, csv, or both.',
                        default='json',
                        choices=['json', 'csv', 'both'])
    parser.add_argument('-r', '--region_id',
                        help='Region id. ie 10000002')
    parser.add_argument('-t', '--type_id',
                        help='Type id. ie. 34')
    # parser.add_argument('-u', '--user',
    #                     help='user name',
    #                     default='root')

    results = parser.parse_args(args)
    return results


def getData() -> str:
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


if __name__ == '__main__':
    results = check_arg()
    outputFolderPath = results.outputFolderPath
    outputFileName = results.outputFileName
    outputFormat = results.outputFormat
    region_id = results.region_id
    type_id = results.type_id
    print(f'p = {outputFolderPath}')
    print(f'n = {outputFileName}')
    print(f'f = {outputFormat}')
    print(f'r = {region_id}')
    print(f't = {type_id}')
    print(f'date string {DATETIMESTRING}')
    data = getData()
    formattedData = formatData(data, outputFormat)
    if outputFolderPath == None:
        print(data)
