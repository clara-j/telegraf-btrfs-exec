import subprocess
import collections

DEBUG = 0


def getPools(excludeList):
     pools = []
     poolsRAW = subprocess.check_output("findmnt -nt btrfs", shell=True)
     poolsLine  = poolsRAW.split('\n')
     for i in range(len(poolsLine)):
          pool = poolsLine[i].split(' ')[0].strip()
          if len(pool) > 1:
               pools.append(pool)
     return pools

def getMeasurements(pool):
    statString = subprocess.check_output("sudo btrfs device stat "+ pool, shell=True)
    statArray = statString.split('\n')
    outArray = []
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
             outArray.append("btrfs,type="+ metric +",drive="+ drive +",pool="+ pool +" value="+ value)
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
    measurments = getMeasurements(pools[i])
    for j in range(len(measurments)):
        print measurments[j]

