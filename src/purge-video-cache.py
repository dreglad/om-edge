#!/usr/bin/env python
"""
This script runs indefinitely.

This script execute a cleaning proccess and once it is finished it waits
5 minutes, by default, before executing it again.
"""
# Time expressed on minutes.
TIME=5
# Maximun percentage of space used.
MAX_USAGE=97
# Percentage of space used expected
EXPECTED_USAGE=90


import os.path
import sys
import time
import logging

from operator import attrgetter
from collections import namedtuple



logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='[%m/%d/%Y %H:%M:%S]',
        level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(sys.argv[0])
logger.debug("Debuging mode enable")


File = namedtuple('File', ['path', 'atime', 'size'])


def fmt(size):
    GB = 1024 * 1024 * 1024 # B * K * G
    return "{0:.2f} Gb".format(size / GB)

def purge():
    return

    files = []
    for obj in os.scandir(STORAGE):
        if obj.is_file(follow_symlinks=False):
            cfile = File(path=obj.path,
                        atime=os.path.getatime(obj.path),
                        size=os.path.getsize(obj.path))

            files.append(cfile)

    # sort files based on atime, last access fisrt and for items with the same
    # atime the less bigger first.
    files.sort(key=attrgetter('size'))
    files.sort(key=attrgetter('atime'), reverse=True)

    total, free, avail, used, p_used, p_avail = stats()
    # desired percentage of use. for math use
    # Ex: 100 - 10 = 90 === 90% === 0.09
    p_target = EXPECTED_USAGE
    # desired amount of Bytes to delete  = total * (desired % free space)
    to_delete = total * (p_used - p_target)
    # desired percentage of use in Bytes
    desired = total * p_target

    deleted = 0
    dfs = []
    while p_target <= p_used:
        while deleted <= to_delete:
            try:
                tdfile = files.pop()
                dfs.append(tdfile)
            except IndexError: # This shold never happen
                logger.error("All files deleted {}. Desired free space"
                             " not reached.".format(fmt(deleted)))
                sys.exit(1)

            os.remove(tdfile.path)
            deleted += tdfile.size
            logger.debug("Deleteing file: {}".format(tdfile.path))

        total, free, avail, used, p_used, p_avail = stats()
        to_delete = total * (p_used - p_target)
        logger.info("size to_delete: {}, deleted: {}, percentage used: {}"
                .format(to_delete, deleted, p_used))

    logger.info("Deleted {} files, {}, {} B.".format(len(dfs), fmt(deleted), deleted))
    for dfile in dsf:
        logger.debug(dfile)


def stats():
    stat = os.statvfs(STORAGE)
    total = (stat.f_bsize * stat.f_blocks)
    free  = (stat.f_bsize * stat.f_bfree)
    avail = (stat.f_bsize * stat.f_bavail)
    used = total - free
    p_used = used * 100 / total
    p_avail = avail * 100 / total

    return total, free, avail, used, p_used, p_avail


def main():
    total, free, avail, used, p_used, p_avail = stats()
    logger.info(
            "Storage: {} | Total: {} | Used: {} (%{:.2f}) | Available: {} (%{:.2f})"
            .format(STORAGE, fmt(total), fmt(used), p_used, fmt(avail), p_avail))

    if p_used >= MAX_USAGE:
        p_toremove = EXPECTED_USAGE - p_used
        logger.info("Removing {} Mb, %{:.2f} of the total space."
                .format(fmt(total * p_toremove * 0.01), p_toremove))
        logger.debug("p_toremove: {}, p_used: {}, MAX_USAGE: {}, EXPECTED_USAGE: {}"
                .format(p_toremove, p_used, MAX_USAGE, EXPECTED_USAGE))
        purge()

        total, free, avail, used, p_used, p_avail = stats()
        logger.info("Storage: {} | Total: {} | Used: {} (%{:.2f}) | Available: {} (%{:.2f})"
                    .format(STORAGE, fmt(total), fmt(used), p_used, fmt(avail), p_avail))
    else:
        logger.debug("Maximun use not reached. No action executed. MAX_USAGE: {}, EXPECTED_USAGE: {}"
                    .format(MAX_USAGE, EXPECTED_USAGE))


if __name__ == '__main__':
    try:
        STORAGE=sys.argv[1]
    except IndexError as e:
        logger.error("You must specify the storage path")
        sys.exit(1)
    else:
        if not os.path.isdir(STORAGE):
            logger.error("The first parameter must be the storage path")
            sys.exit(2)

    if len(sys.argv) >= 3:
        TIME = int(sys.argv[2])
        logger.debug("TIME: {}".format(TIME))
    if len(sys.argv) >= 4:
        MAX_USAGE = int(sys.argv[3])
        logger.debug("MAX_USAGE: {}".format(MAX_USAGE))
    if len(sys.argv) >= 5:
        EXPECTED_USAGE = int(sys.argv[4])
        logger.debug("EXPECTED_USAGE: {}".format(EXPECTED_USAGE))


    while True:
        main()
        logger.debug("Sleep TIME: {} minutes.".format(TIME))
        time.sleep(TIME * 60)
