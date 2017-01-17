#!/usr/bin/python

import os
import psutil
import sys

from charmhelpers.core.hookenv import action_get, log, config, action_fail

from ceph import unmounted_disks

stats_intervals = ['stats_day', 'stats_five_minute',
                   'stats_hour', 'stats_total']

def get_bcache_fs():
    try:
        dirs = os.listdir('/sys/fs/bcache')
    except OSError:
        log("No bcache fs found")
        return []
    sets = [d for d in dirs if not d.startswith('register')]
    return sets

def fmt(elem, val):
    return "{}: {}".format(elem, val)

def get_stats(devpath, interval):
    intervaldir = 'stats_{}'.format(interval)
    path = os.path.join(devpath, intervaldir)
    out = []
    for elem in os.listdir(path):
        out.append(
            fmt(elem, 
            open(os.path.join(path, elem)).read().strip()))
    return '\n'.join(out)


if __name__ == '__main__':
    interval = action_get("interval")
    osd_devices = action_get("osd-devices")
    action_set({
        'stats': get_stats()})

