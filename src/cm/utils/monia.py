# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end

"""@package src.cm.manager.utils
@author Tomek Wojtoń
"""

import os.path
import tarfile
import time

from cm import settings
from cm.utils import log
from cm.utils.exception import CMException
import rrdtool


def check_stat_exists(vm):
    try:
        rrdtool.info(get_path(vm))
    except Exception, e:
        log.error(0, 'stat_error %s %s' % (vm, e))
        return 0
    return 1


def get_path(vm):
    path = settings.PATH_TO_RRD + vm + '.rrd'
    return path


def get_backup_path(vm):
    return settings.BACKUP_PATH + vm + '.tar.gz'


def stat_unit(stat_name):
    d = {
        'cpu_count': 'num',
        'cpu_time': 'time',
        'rd_req': 'ops',
        'rd_bytes': 'bytes',
        'wr_req': 'ops',
        'wr_bytes': 'bytes',
        'rx_bytes': 'bytes',
        'rx_packets': 'ops',
        'tx_bytes': 'bytes',
        'tx_packets': 'ops',
      }
    return d[stat_name]


class RingBuffer(list):
    def add(self, x):
        if not x in self:
            self.append(x)
            log.debug(0, '%s added' % str(x))
        else:
            log.debug(0, '%s exists' % str(x))

    def clear(self):
        self[:] = []

    def get(self):
        try:
            t = self.pop(0)
            self.append(t)
            return t
        except Exception, e:
            log.exception(0, e)


class RrdHandler():
    def __init__(self, data=None):
        if data:
            self.vm = data
            self.filepath = get_path(data['name'])
            self.backuppath = get_backup_path(data['name'])

    def update(self):
        """
        Update rrd file, if exists. Otherwise create new rrd
        """
        if not self.vm:
            raise Exception('No VM specified')
        try:
            filesize = os.path.getsize(self.filepath)
        except Exception:
            filesize = 0

        if(filesize == 0):
            self.create()
        else:  # appropriate updating
            ret = rrdtool.update("%s" % (self.filepath), 'N:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d' % (int(self.vm['cpu_count']),
                int(self.vm['cpu_time']) / 100000000 / 10.0 / self.vm['cpu_count'],
                int(self.vm['rd_req']),
                int(self.vm['rd_bytes']),
                int(self.vm['wr_req']),
                int(self.vm['wr_bytes']),
                int(self.vm['rx_bytes']),
                int(self.vm['rx_packets']),
                int(self.vm['tx_bytes']),
                int(self.vm['tx_packets']),
                ))
            if ret:
                log.error(0, 'update error: %s' % (rrdtool.error()))

    def create(self):
        if not self.vm:
            raise Exception('No VM specified')
        rarg = ["%s" % (self.filepath), "--step", "%d" % settings.PERIOD,
            "DS:cpu_count:GAUGE:%d:0:100000" % (settings.PERIOD * 2),
            "DS:cpu_time:COUNTER:%d:0:100000" % (settings.PERIOD * 2),
            "DS:rd_req:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            "DS:rd_bytes:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            "DS:wr_req:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            "DS:wr_bytes:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            "DS:rx_bytes:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            "DS:rx_packets:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            "DS:tx_bytes:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            "DS:tx_packets:COUNTER:%d:0:100000000" % (settings.PERIOD * 2),
            ]
        for s in settings.STATS:
            rarg.append("RRA:AVERAGE:0.5:%d:%d" % (s[0], s[1]))

        try:
            ret = rrdtool.create(rarg)  # all data = 3,1MB
            if ret:
                log.error(0, 'update error: %s' % (rrdtool.error()))
        except Exception, e:
            log.exception(0, e)
        log.info(0, 'created: %s' % (self.filepath))

    def remove(self):
        if not self.vm:
            return 0

        tar = tarfile.open(self.backuppath, "w:gz")
        tar.add(self.filepath)
        tar.close()

        os.remove(self.filepath)
        log.info(0, 'removed: %s -> %s' % (self.filepath, self.backuppath))

    def get_list(self):
        """
        list vm stats with start and end times
        """
        f = os.listdir(settings.PATH_TO_RRD)

        rrds = {}
        for rrd in f:
            try:
                t = []
                t.append(rrdtool.first(settings.PATH_TO_RRD + rrd))
                t.append(rrdtool.last(settings.PATH_TO_RRD + rrd))
                rrds.update({os.path.splitext(rrd)[0]: t})
            except Exception, e:
                log.error(0, 'stat_error %s %s' % (rrd, e))
        return rrds

    def get_vm_info(self, vm):
        """
        return information about steps, start & end time,
        and available stats

        time: 190us
        faster than regex
        """
        if not check_stat_exists(vm):
            raise CMException('stat_not_exists')
        filepath = get_path(vm)
        try:
            ds_info = rrdtool.info(filepath)
        except Exception, e:
            log.exception(0, e)
            return 0

        stats = []
        res = []
        step = ds_info['step']

        for key in ds_info.keys():
            if 'index' in key:
                if key[0:2] == "ds":
                    ds_name = key[3:]
                    ds_name = ds_name[0: ds_name.find(']')]
                    stats.append(ds_name)
            if 'pdp_per_row' in key:
                res.append(ds_info[key] * step)
        first = rrdtool.first(filepath)
        last = rrdtool.last(filepath)

        return {'stats': stats, 'resolutions': res, 'first': first, 'last': last}

    def get_vm_stats(self, vm, names, start="-5min", end="now", resolution="10"):
        if not check_stat_exists(vm):
            raise CMException('stat_not_exists')

        res = []
        filename = get_path(vm)
        info, ds_rrd, data = rrdtool.fetch(filename, "AVERAGE", "--start", str(start), "--end", str(end), "--resolution", str(resolution))
        start_rrd = info[0]
        end_rrd = info[1]
        step = info[2]
        ts = start_rrd
        total = self.get_vm_total(vm, names)

        now = int(time.time())

        ds_req = {}
        ds_info = ['timestamp']
        ds_n = []
        ds_u = []
        for i in range(len(ds_rrd)):
            ds = ds_rrd[i]
            if ds in names:
                ds_req[i] = names.index(ds)
                ds_n.append(ds)
                ds_u.append(stat_unit(ds))
        ds_info.append(ds_n)
        ds_info.append(ds_u)
        ds_info.append(end)
        ds_info.append(ts)
        ds_info.append(total.values())
        res.append(ds_info)

        for row in data:
            val = [None for i in names]
            for i in range(len(row)):
                if ds_req.has_key(i):
                    if row[i] == None:
                        val[ds_req[i]] = ''
                    else:
                        val[ds_req[i]] = row[i]
            val.insert(0, ts)
            res.append(val)
            ts = ts + step
            if ts > now - step:
                break
        if end_rrd > now + step:
            res.append([ts + step, ''])
            res.append([end_rrd, ''])
        return res

    def get_vm_last(self, vm, res):
        if not check_stat_exists(vm):
            raise CMException('stat_not_exists')
        vm_id = get_path(vm)
        r = rrdtool.fetch("%s" % vm_id, 'AVERAGE', '-r', str(res), '-s', '-%ds' % (int(res) * 2), '-e', 'now')
        i = {}
        i['epoch'] = r[0][0]
        i['labels'] = r[1]
        i['data'] = map(lambda d: "" if d is None else d, r[2][0])
        ret = dict(zip(i['labels'], i['data']))

        return ret

    def get_vm_total(self, vm, names=['cpu_time', 'rd_req', 'rd_bytes', 'wr_req', 'wr_bytes', 'rx_bytes', 'tx_bytes']):
        if not check_stat_exists(vm):
            raise CMException('stat_not_exists')
        filename = get_path(vm)
        ds_info = rrdtool.info(filename)

        ds_all = {}
        for i in names:
            ds_all[i] = ds_info['ds[%s].last_ds' % i]
        return ds_all

    def cpu_load(self, vm, periods):
        if not check_stat_exists(vm):
            raise CMException('stat_not_exists')
        r = {}
        res = self.get_vm_info(vm)['resolutions']
        min_res = min(res)
        vm_id = get_path(vm)

        for p in periods:
            try:
                d = self.get_vm_stats(vm, ['cpu_time'], '-%ds' % (long(p) + min_res), 'now', min_res)
            except Exception, e:
                d = []

            if not d:
                continue
            cpus = [i[1] for i in d[1:] if i[1] != '']
            if len(cpus):
                r.update({str(p): "%.2f" % (sum(cpus) / float(len(cpus)))})
        return r
