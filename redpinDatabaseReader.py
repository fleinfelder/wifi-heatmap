import ConfigParser
import MySQLdb as mdb
import dbRequest
import sys

config = ConfigParser.SafeConfigParser()
config.read(['./redpin.cfg'])
dbapi = config.get('db', 'dbapi')
dbhost = config.get('db', 'dbhost')
dbname = config.get('db', 'dbname')
dbuser = config.get('db', 'dbuser')
dbpass = config.get('db', 'dbpass')


class dbAccess:

    con = None
    dbr = None

    def __init__(self):
        try:
            self.con = mdb.connect(dbhost, dbuser, dbpass, dbname)
            self.dbr = dbRequest.dbRequest(self.con)

        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)

    def getMaps(self, assoc=False):
        return self.dbr.fetchAsArray("SELECT * FROM `map` ORDER BY `mapId`", assoc)

    def getAPsForMap(self, mapId, assoc=False):
        sql = "SELECT `bssid`, `ssid`, MAX(`rssi`) as max FROM `wifireading` JOIN `readinginmeasurement` ON `readinginmeasurement`.`readingId`=`wifireading`.`wifireadingId` JOIN `fingerprint` USING(`measurementId`) JOIN `location` USING (`locationId`) WHERE `mapId`=%d GROUP BY `bssid`" % mapId
        return self.dbr.fetchAsArray(sql, assoc)

    def getDatasetForAP(self, macAddress, assoc=False):
        sql = "SELECT `mapXCord` AS x, `mapYCord` AS y, `rssi` FROM `location` JOIN `fingerprint` USING (`locationId`) JOIN `readinginmeasurement` USING (`measurementId`) JOIN `wifireading` ON `readinginmeasurement`.`readingId`=`wifireading`.`wifireadingId` WHERE `bssid`='%s' AND `mapXCord`!= 0 AND mapYCord != 0" % macAddress
        return self.dbr.fetchAsArray(sql, assoc)

    def getDatasetForMap(self, mapId, assoc=False):
        sql = "SELECT `mapXCord` AS x, `mapYCord` AS y, `rssi`, `bssid` FROM `wifireading` JOIN `readinginmeasurement` ON `readinginmeasurement`.`readingId`=`wifireading`.`wifireadingId` JOIN `measurement` USING(`measurementId`) JOIN `fingerprint` USING(`measurementId`) JOIN `location` USING(`locationId`) WHERE `mapId` = %d AND `mapXCord` != 0 AND `mapYCord` != 0 ORDER BY `locationId`" % mapId
        return self.dbr.fetchAsArray(sql, assoc)

    def getFusedDatasetForMap(self, mapId, assoc=False):
        sql = "SELECT COUNT(`rssi`) AS count, `mapXCord` AS x, `mapYCord` AS y, MIN(`rssi`) AS min, MAX(`rssi`) AS max, CAST(AVG(`rssi`) AS SIGNED) AS avg, STD(`rssi`) AS std_dev, VARIANCE(`rssi`) AS var, `bssid`, `measurementId` FROM `wifireading` JOIN `readinginmeasurement` ON `readinginmeasurement`.`readingId`=`wifireading`.`wifireadingId` JOIN `measurement` USING(`measurementId`) JOIN `fingerprint` USING(`measurementId`) JOIN `location` USING(`locationId`) WHERE `mapId` = %d AND `mapXCord` != 0 AND `mapYCord` != 0 GROUP BY `x`, `y`, `bssid` ORDER BY x, y ASC" % mapId
        return self.dbr.fetchAsArray(sql, assoc)

    def close(self):
        self.con.close()
