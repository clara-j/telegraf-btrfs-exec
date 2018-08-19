import subprocess
import collections

DEBUG = 0


def getPools(excludeList):
     pools = []
     poolsRAW = subprocess.check_output("findmnt -o TARGET --list -nt  btrfs", shell=True)
     poolsLine  = poolsRAW.split('\n')
     for i in range(len(poolsLine)):
          pool = poolsLine[i].replace('\xe2','').replace('\xe2','').split(' ')[0].strip()
          if len(pool) > 0:
               pools.append(pool)
     return pools

def getFileSystemDFMeasurements(pool):
    commandString = subprocess.check_output("sudo btrfs filesystem df -b " + pool, shell=True)

    btrfsType = "df"

    outArray = []

    #split into section
    commandArray = commandString.split('\n')


    for i in range(len(commandArray)):
        lineSections =  commandArray[i].replace(':',',').split(',')
        if len(lineSections) > 1:
            metric = lineSections[0].strip()
            raidType = lineSections[1].strip()
            total = lineSections[2].strip()
            used = lineSections[3].strip()
            free = str(long(total.split('=')[1]) - long(used.split('=')[1]))

            outArray.append( "btrfs,command=" + btrfsType + ",type=" + metric + ",raidType="+ raidType +",pool=" + pool + " " + total)
            outArray.append( "btrfs,command=" + btrfsType + ",type=" + metric + ",raidType="+ raidType +",pool=" + pool + " " + used)
            outArray.append( "btrfs,command=" + btrfsType + ",type=" + metric + ",raidType=" + raidType + ",pool=" + pool + " free=" + free)

    return outArray

def getFileSystemUsageMeasurements(pool):
    commandString = subprocess.check_output("sudo btrfs filesystem usage -b " + pool, shell=True)
    btrfsType = "usage"
    outArray = []

    #split into section
    sectionArray = commandString.split('\n\n')


    for i in range(len(sectionArray)):
        #split into rows
        measurementLines  = sectionArray[i].split('\n')
        if "Overall:" in measurementLines[0]:
            for j in range(1, len(measurementLines)):
                measurementLinesSection = measurementLines[j].split(':')
                metric = measurementLinesSection[0].strip().replace(' ', '_')
                value = measurementLinesSection[1].strip().split('\t')[0]
                outArray.append("btrfs,command=" + btrfsType + ",type="+ metric +",pool="+ pool +" value="+ value)
        else:
            type = measurementLines[0].replace(':',',').split(',')[0]
            for j in range(1, len(measurementLines)):
                if len(measurementLines[j]) > 1:
                    measurementLinesSection = measurementLines[j].strip().split('\t')
                    drive = measurementLinesSection[0].strip()
                    value = measurementLinesSection[1].strip()
                    if DEBUG:
                        print("Drive: " + drive)
                        print("Type: " + type)
                        print("Value: " + value)
                    outArray.append("btrfs,command=" + btrfsType + ",type="+ type +",drive="+ drive +",pool="+ pool +" value="+ value)

    return outArray


def getDeviceStatMeasurements(pool):
    statString = subprocess.check_output("sudo btrfs device stat "+ pool, shell=True)
    statArray = statString.split('\n')
    outArray = []
    btrfsType = "stat"

    for i in range(len(statArray)):
        a = statArray[i].split()
        if len(a) > 1:
             b = a[0].split('.')
             drive = b[0].replace("[","").replace("]","")
             metric = b[1]
             value = a[1]
             if DEBUG:
                print("Drive: "+ drive)
                print("Metric: "+ metric)
                print("Value: "+ value)
             outArray.append("btrfs,command=" + btrfsType + ",type="+ metric +",drive="+ drive +",pool="+ pool +" value="+ value)
    return outArray


excludeList = []
pools = getPools(excludeList)

if DEBUG:
    print "----------- Pools -----------"
    print pools
    print "----------- Pools -----------"


for i in range(len(pools)):
    if DEBUG:
        print "----------- Measurements -----------"
        print "Pool: "+ pools[i]
    deviceStatMeasurements = getDeviceStatMeasurements(pools[i])
    for j in range(len(deviceStatMeasurements)):
        print deviceStatMeasurements[j]

    filesystemDFMeasurements = getFileSystemDFMeasurements(pools[i])
    for j in range(len(filesystemDFMeasurements)):
        print filesystemDFMeasurements[j]

    filesystemUsageMeasurements = getFileSystemUsageMeasurements(pools[i])
    for j in range(len(filesystemUsageMeasurements)):
        print filesystemUsageMeasurements[j]
