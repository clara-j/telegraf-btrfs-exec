#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
import shutil
import subprocess
log = logging.getLogger("telegraf-btrfs")
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
logformat = "%(message)s"
formatter = logging.Formatter(logformat)
ch.setFormatter(formatter)
log.addHandler(ch)


def _find_binaries():
    findmnt = shutil.which("findmnt")
    btrfs = shutil.which("btrfs")
    sudo = shutil.which("sudo")
    return btrfs, findmnt, sudo


def getPools(excludeList, find_path="findmnt"):
    poolsRAW = subprocess.Popen([find_path, "-o", "TARGET", "--list",
                                 "-nt", "btrfs"],
                                stdout=subprocess.PIPE)
    output = poolsRAW.communicate()[0].decode("utf-8")
    output = [p for p in output.split("\n")
              if p and p not in excludeList]
    return output


def getFileSystemDFMeasurements(pool, sudo="sudo", btrfs="btrfs"):
    commandString = subprocess.Popen([sudo, btrfs, "filesystem", "df",
                                      "-b", pool],
                                     stdout=subprocess.PIPE)
    btrfsType = "df"
    # split into section
    for line in commandString.communicate()[0].decode("utf-8").split('\n'):
        if not line:
            continue
        lineSections = line.replace(':', ',').split(',')
        if len(lineSections) > 1:
            metric = lineSections[0].strip()
            raidType = lineSections[1].strip()
            total = lineSections[2].strip()
            used = lineSections[3].strip()
            free = int(total.split('=')[1]) - int(used.split('=')[1])
            output = "btrfs,command={},".format(btrfsType)
            output += "type={},".format(metric)
            output += "raidType={},".format(raidType)
            output += "pool={}".format(pool)
            print("{} total={},used={},free={}".format(output, total,
                                                       used, free))


def getFileSystemUsageMeasurements(pool, sudo="sudo", btrfs="btrfs"):
    commandString = subprocess.Popen([sudo, btrfs, "filesystem", "usage",
                                      "-b", pool],
                                     stdout=subprocess.PIPE)
    btrfsType = "usage"
    output = "btrfs,command={},pool={}".format(btrfsType, pool)
    # split into section
    commandArray = commandString.communicate()[0].decode("utf-8").split('\n\n')
    for section in commandArray:
        # split into rows
        measurementLines = section.split('\n')
        if "Overall:" in measurementLines[0]:
            # skip the "overall" section with a slice
            for j in measurementLines[1:]:
                if "Multiple_profiles" in metric:
                    continue
                measurementLinesSection = j.split(':')
                metric = measurementLinesSection[0].strip()
                metric = metric.replace(' ', '_').lower()
                metric = metric.replace("_(estimated)", "")
                value = measurementLinesSection[1].strip().split('\t')[0]
                print("{} {}={}".format(output, metric, value))
        else:
            btype = measurementLines[0].replace(':', ',').split(',')[0]
            for j in measurementLines[1:]:
                if len(j) > 1:
                    measurementLinesSection = j.strip().split('\t')
                    drive = measurementLinesSection[0].strip()
                    value = measurementLinesSection[1].strip()
                    log.debug("Drive: {}, Type: {}, Value: {}".format(drive,
                                                                      btype,
                                                                      value))
                    outputstr = "{},drive={}".format(output, drive)
                    print("{} {}={}".format(outputstr, btype, value))


def getDeviceStatMeasurements(pool, sudo="sudo", btrfs="btrfs"):
    statString = subprocess.Popen([sudo, btrfs, "device", "stat", pool],
                                  stdout=subprocess.PIPE)
    statArray = statString.communicate()[0].decode("utf-8").split('\n')
    btrfsType = "stat"
    output = "btrfs,command={},pool={}".format(btrfsType, pool)
    for stat in statArray:
        a = stat.split()
        if len(a) > 1:
            b = a[0].split('.')
            drive = b[0].replace("[", "").replace("]", "")
            metric = b[1]
            value = a[1]
            log.debug("Drive: {}, Metric: {}, Value: {}".format(drive,
                                                                metric,
                                                                value))
            outputstr = "{},drive={}".format(output, drive)
            print("{} {}={}".format(outputstr, metric, value))


def cli_opts():
    parser = ArgumentParser(description="Collect stats from btrfs volumes",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Show debug information")
    parser.add_argument("-e", "--exclude-pools", default="",
                        help="arrays/mounts to exclude (comma-separated)")
    return parser.parse_args()


if __name__ == "__main__":
    args = cli_opts()
    if args.debug:
        log.setLevel(logging.DEBUG)
    btrfs, findmnt, sudo = _find_binaries()
    exclude = args.exclude_pools.split(",")
    pools = getPools(args.exclude_pools, findmnt)
    log.debug(pools)

    for pool in pools:
        log.debug("Processing {}".format(pool))
        getDeviceStatMeasurements(pool)
        getFileSystemDFMeasurements(pool)
        getFileSystemUsageMeasurements(pool)
