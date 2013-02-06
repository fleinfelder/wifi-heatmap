import ConfigParser
import redpinDatabaseReader
import urllib
import csv
import sys

db = redpinDatabaseReader.dbAccess()
dataset = None
config = ConfigParser.SafeConfigParser()
config.read(['./redpin.cfg'])
imageFilename = config.get('input', 'imageFilename')
csvFilename = config.get('input', 'csvFilename')

fusionFunctions = ['min', 'max', 'avg', 'std_dev', 'var']
noiseLevel = -100


def selectMapId():
    maps = db.getMaps(assoc=True)
    for row in maps:
        print "%d) %s" % (row['mapId'], row['mapName'])
    mapId = raw_input("Select Map: ")
    return int(mapId)


def selectFusionFunction():
    number = 1
    for func in fusionFunctions:
        print "%d) %s" % (number, func)
        number = number + 1
    f = raw_input("Select Fusion Function: ")
    return fusionFunctions[int(f) - 1]


def readRedpinData(mapId):
    global dataset
    maps = db.getMaps(assoc=True)
    for row in maps:
        if row['mapId'] == mapId:
            mapURL = row['mapURL']
    # Donwload Map to input folder
    urllib.urlretrieve(mapURL, imageFilename)
    # Save dataset locally
    dataset = db.getFusedDatasetForMap(mapId, True)


def exportDataToCSV(mapId, fusionFunction):

    def _selectFusionFunction(fusionFunction):
        # check for fusion Function, default is average
        if (fusionFunction in fusionFunctions):
            return fusionFunction
        else:
            return 'avg'

    def _openFile(filename):
        return open(filename, 'wb')

    def _closeFile(fileHandler):
        fileHandler.close()

    def _createWriter(file):
        return csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    def _writeHeader(writer):
        header = ['Grid Position', 'Drawing X', 'Drawing Y']
        for row in aps:
            header.append(row[0])
        writer.writerow(header)

    def _newCache():
        # init cache to noiseLevel
        cache = {}
        for ap in aps:
            cache[ap[0]] = noiseLevel
        return cache

    def _writeLine(writer, cache):
        # write dache to csv file
        out = [count, x, y]
        for ap in aps:
            out.append(cache[ap[0]])
        writer.writerow(out)

    x = 0
    y = 0
    count = 0
    aps = db.getAPsForMap(mapId)
    func = _selectFusionFunction(fusionFunction)
    file = _openFile(csvFilename)
    writer = _createWriter(file)
    _writeHeader(writer)

    cache = _newCache()
    for row in dataset:
        if x != row['x'] or y != row['y']:
            # new coordinates => construct line and write old line (cache)
            if count > 0:
                _writeLine(writer, cache)
            # clear cache
            cache = _newCache()
            x = row['x']
            y = row['y']
            count = count + 1
        # for every row in dataset add fused rssi value to dache
        cache[row['bssid']] = row[func]

    _closeFile(file)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        mapId = selectMapId()
        fusionFunction = selectFusionFunction()
    else:
        mapId = int(sys.argv[1])
        fusionFunction = sys.argv[2]
    readRedpinData(mapId)
    exportDataToCSV(mapId, fusionFunction)
    db.close()
