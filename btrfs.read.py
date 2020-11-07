#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
import re
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


def scrub_stats(pool, sudo="sudo", btrfs="btrfs"):
    """
    scrub status for b24cf3ce-6063-4c63-8141-8c080e6d9bf4
        # one of the following:
         no stats available
         scrub started at Sat Nov  7 21:24:20 2020, running for 00:00:25
         scrub started at Fri Nov  6 06:15:01 2020 and finished after 00:00:30
        data_extents_scrubbed: 275088
        tree_extents_scrubbed: 9942
        data_bytes_scrubbed: 10591723520
        tree_bytes_scrubbed: 162889728
        read_errors: 0
        csum_errors: 0
        verify_errors: 0
        no_csum: 1958
        csum_discards: 0
        super_errors: 0
        malloc_errors: 0
        uncorrectable_errors: 0
        unverified_errors: 0
        corrected_errors: 0
        last_physical: 17235443712
    """
    commandString = subprocess.Popen([sudo, btrfs, "scrub", "status",
                                      "-R", pool],
                                     stdout=subprocess.PIPE)
    start_match = re.compile("")
    running_match = re.compile(".*running for (.*)")
    finished_match = re.compile(".*finished after (.*)")
    output = "btrfs_scrub,pool={} ".format(pool)
    for line in commandString.communicate()[0].decode("utf-8").split("\n"):
        line = line.strip()
        if not line or any(line.startswith(s) for s in ["scrub status",
                                                        "no stats"]):
            continue
        if line.startswith("scrub started"):
            running = running_match.search(line)
            finished = finished_match.search(line)
            log.debug("Running time: {}, Finished time: {}".format(running,
                                                                   finished.group(0)))
            # start 
        else:
            log.debug("processing {}".format(line))
            key, value = line.split(":")
            output += "{}={},".format(key.strip(), value.strip())
    print(output.strip(","))


def getFileSystemDFMeasurements(pool, sudo="sudo", btrfs="btrfs"):
    """
    Data, single: total=13967032320, used=10596143104
    System, single: total=67108864, used=16384
    Metadata, single: total=2155872256, used=163217408
    GlobalReserve, single: total=26869760, used=0
    """
    commandString = subprocess.Popen([sudo, btrfs, "filesystem", "df",
                                      "-b", pool],
                                     stdout=subprocess.PIPE)
    # split into section
    for line in commandString.communicate()[0].decode("utf-8").split("\n"):
        if not line:
            continue
        lineSections = line.replace(":", ",").split(",")
        if len(lineSections) < 2:
            continue
        metric = lineSections[0].strip()
        raidType = lineSections[1].strip()
        total = lineSections[2].strip()
        used = lineSections[3].strip()
        free = int(total.split("=")[1]) - int(used.split("=")[1])
        output = "btrfs_df,type={},raidType={},pool={}".format(metric,
                                                               raidType,
                                                               pool)
        print("{} {},{},free={}".format(output, total,
                                        used, free))


def getFileSystemUsageMeasurements(pool, sudo="sudo", btrfs="btrfs"):
    """
    Overall:
        Device size:		      245823963136
        Device allocated:		       16190013440
        Device unallocated:		      229633949696
        Device missing:		                 0
        Used:			       10759409664
        Free (estimated):		      233004806144	(min: 233004806144)
        Data ratio:			              1.00
        Metadata ratio:		              1.00
        Global reserve:		          26869760	(used: 0)

    Data,single: Size:13967032320, Used:10596175872
       /dev/md125	13967032320

    Metadata,single: Size:2155872256, Used:163217408
       /dev/md125	2155872256

    System,single: Size:67108864, Used:16384
       /dev/md125	  67108864

    Unallocated:
       /dev/md125	229633949696
    """
    commandString = subprocess.Popen([sudo, btrfs, "filesystem", "usage",
                                      "-b", pool],
                                     stdout=subprocess.PIPE)
    output = "btrfs_usage,pool={}".format(pool)
    # split into section
    commandArray = commandString.communicate()[0].decode("utf-8").split("\n\n")
    drives = {}
    for section in commandArray:
        # split into rows
        measurementLines = section.split("\n")
        if "Overall:" in measurementLines[0]:
            # skip the "overall" section with a slice
            outputstr = "{} ".format(output)
            for j in measurementLines[1:]:
                if "Multiple_profiles" in j:
                    continue
                measurementLinesSection = j.split(":")
                metric = measurementLinesSection[0].strip()
                metric = metric.replace(" ", "_").lower()
                metric = metric.replace("_(estimated)", "")
                value = measurementLinesSection[1].strip().split("\t")[0]
                outputstr += "{}={},".format(metric, value)
            print(outputstr.strip(","))
        else:
            btype = measurementLines[0].replace(":", ",").split(",")[0]
            for j in measurementLines[1:]:
                if len(j) < 2:
                    continue
                measurementLinesSection = j.strip().split("\t")
                drive = measurementLinesSection[0].strip()
                value = measurementLinesSection[1].strip()
                log.debug("Drive: {}, Type: {}, Value: {}".format(drive,
                                                                  btype,
                                                                  value))
                if drive in drives:
                    drives[drive][btype] = value
                else:
                    drives[drive] = {btype: value}
    for drive, data in drives.items():
        outputstr = "{},drive={} ".format(output, drive)
        for k, v in data.items():
            outputstr += "{}={},".format(k, v)
        print(outputstr.strip(","))


def getDeviceStatMeasurements(pool, sudo="sudo", btrfs="btrfs"):
    """
    [/dev/md125].write_io_errs    0
    [/dev/md125].read_io_errs     0
    [/dev/md125].flush_io_errs    0
    [/dev/md125].corruption_errs  0
    [/dev/md125].generation_errs  0
    """
    statString = subprocess.Popen([sudo, btrfs, "device", "stat", pool],
                                  stdout=subprocess.PIPE)
    statArray = statString.communicate()[0].decode("utf-8").split('\n')
    output = "btrfs_stat,pool={}".format(pool)
    drives = {}
    for stat in statArray:
        a = stat.split()
        if len(a) < 2:
            continue
        b = a[0].split('.')
        drive = b[0].replace("[", "").replace("]", "")
        metric = b[1]
        value = a[1]
        log.debug("Drive: {}, Metric: {}, Value: {}".format(drive,
                                                            metric,
                                                            value))
        if drive in drives:
            drives[drive][metric] = value
        else:
            drives[drive] = {metric: value}
    for drive, data in drives.items():
        outputstr = "{},drive={} ".format(output, drive)
        for k, v in data.items():
            outputstr += "{}={},".format(k, v)
        print(outputstr.strip(","))


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
        try:
            getDeviceStatMeasurements(pool)
        except Exception as e:
            log.debug("Failed to collect stats for {} :: {}".format(pool, e))
        try:
            getFileSystemDFMeasurements(pool)
        except Exception as e:
            log.debug("Failed to collect df for {} :: {}".format(pool, e))
        try:
            getFileSystemUsageMeasurements(pool)
        except Exception as e:
            log.debug("Failed to collect usage for {} :: {}".format(pool, e))
        try:
            scrub_stats(pool)
        except Exception as e:
            log.debug("Failed to collect scrubs for {} :: {}".format(pool, e))
