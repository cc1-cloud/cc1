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

"""@package src.cm.manager.monia.threads

@author Tomek Wojtoń
"""

import threading
import libvirt
import time
import sys
import os
from cm.utils.monia import RrdHandler
from xml.dom.minidom import parse, parseString
import cm.utils.monia
import rrdtool
from cm.models.node import Node
from common.states import node_states
from cm.utils import log
from cm import settings


def get_nodes():
    nlist = [{'address':node.dict['address'], 'state':node.dict['state'], 'conn_string':node.conn_string}  for node in Node.objects.filter(state__exact=node_states['ok'])]

    return nlist


def refresh_nodes():
    if not settings.MONITOR_ENABLE:
        return 'Monitoring disabled'
    nlist = get_nodes()
    if not nlist:
        return 'No nodes to monitor'
    e=threading.enumerate()
    for i in e:
        if i.name == "initiator":
            i.update_nodes(nlist)
    return nlist


def start_monia():
    """
    Starts the system monitoring
    @response (list)
    """
    if not settings.MONITOR_ENABLE:
        stop_monia()
        return 'Monitoring disabled'
    nlist = get_nodes()
    if not nlist:
        stop_monia()
        return 'No nodes to monitor'
    r=[]
    e=threading.enumerate()

    #update list of nodes in MonitorInitiator thread
    for t in e:
        if t.name == "initiator":
            t.update_nodes(nlist)
            log.info(0, 'Monitoring nodes list updated')
            r.append('node list updated')

    #start MonitorInitiator thread...
    if not [t for t in e if t.name == 'initiator']:
        monitor = MonitorInitiator()
        monitor.start()
        monitor.join()
        r.append('initiator started')
        log.info(0, 'Monitoring thread MonitorInitiator started')

    #start CleanerThread thread...
    if not [t for t in e if t.name == 'cleaner']:
        cl=CleanerThread()
        cl.start()
        cl.join()
        r.append('cleaner started')
        log.info(0, 'Monitoring thread CleanerThread started')

    #log.info(0, 'Monitoring threads %s started' % str(r))
    return r


def stop_monia():
    """
    Stop the monitoring system
    @response (list)
    """

    t=threading.activeCount()
    e=threading.enumerate()
    th=[]
    for i in e:
        th.append(i.getName())
        if i.getName() == "initiator":
            i.kill()
        if i.getName() == "cleaner":
            i.kill()
    log.info(0, 'Monitoring threads stopped')
    return [str(t), str(th)]


class MonitorInitiator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.name= "initiator"
        self.running = True
        if not cm.utils.monia.os.path.exists(settings.PATH_TO_RRD):
            cm.utils.monia.os.makedirs(settings.PATH_TO_RRD)
        if not cm.utils.monia.os.path.exists(settings.BACKUP_PATH):
            cm.utils.monia.os.makedirs(settings.BACKUP_PATH)

        self.rb = cm.utils.monia.RingBuffer()

        nlist = get_nodes()
        self.frequency = settings.PERIOD*1.0/len(nlist)
        for n in nlist:
            self.rb.add(n)
        #self.start()

    def update_nodes(self, nlist):
        log.info(0, 'updating nodes list')
        self.rb.clear()
        for n in nlist:
            self.rb.add(n)

    def run(self):
            while self.running:
                try:
                    one=self.rb.get()
                    if not one['address'] in [i.name for i in threading.enumerate()]:
                        t = MonitorThread(one)
                        t.start()
                except Exception, e:
                    log.error(0, 'Monitoring error %s: %s'%(one['address'],e))
                time.sleep(self.frequency)
            log.info(0, "MonitorInitiator stopped")

    def kill(self):
        log.info(0, "stopping MonitorInitiator... ")
        self.running = False
        # sys.exit()


class CleanerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.name="cleaner"
        self.running = True

    def kill(self):
        log.info(0, "stopping CleanerThread... ")
        self.running = False
        # sys.exit()

    def run(self):
        try:
            while self.running:
                time.sleep(settings.CLEANING_PERIOD)
                rrds=cm.utils.monia.RrdHandler().get_list()
                for vm in rrds:
                    if time.time()-settings.TIME_TO_REMOVE > rrds[vm][1]:
                        cm.utils.monia.RrdHandler({'name': str(vm), 'data': None}).remove()
            log.info(0, "CleanerThread stopped")
        except Exception, e:
            log.exception(0, 'CleanerThread: %s'%(e))


class MonitorThread(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.addr = data['conn_string']
        self.name = data['address']
        self.setDaemon(True)
        self.t = threading.Timer(settings.TIMEOUT,self.kill)
        self.t.name='timer-%s' %(self.name)

    def run(self):
        start = time.time()
        self.update()
        #log.debug(0, 'Checking node: %s'%(self.getName()))

    def update(self):
        r=self.read_node()
        if not r:
            return r
        vm_list = r[4]
        if vm_list:
            for vm in vm_list:
                cm.utils.monia.RrdHandler(vm).update()

    def read_node(self):
        used_cpu = 0
        used_memory = 0
        try:
            self.c = libvirt.openReadOnly(self.addr)
            total_cpu = self.c.getInfo()[2]
            total_memory = self.c.getInfo()[1]
        except Exception, e:
            log.error(0, 'libvirt getting info: %s'%(e))
            return None
        vms=[]

        try:
            domains = self.c.listDomainsID()
        except Exception, e:
            log.exception(0, 'libvirt listDomainsID: %s'%(str(e)))
            return None

        for id in domains:
            try:
                hostname = self.c.getHostname()
                dom = self.c.lookupByID(id)
                info = dom.info() #struct virDomainInfo
                used_cpu += info[3]
                used_memory += info[1]
                self.xml_data = parseString(dom.XMLDesc(0))
                xml_nodes = self.xml_data.childNodes
                try:
                    hdd = xml_nodes[0].getElementsByTagName("devices")[0].getElementsByTagName("disk")[0].getElementsByTagName("target")[0].getAttribute("dev")
                    hdd_stat = dom.blockStats(hdd)
                except Exception:
                    hdd_stat = [0,0,0,0,0,0,0,0,0,0,0,0,0]
                try:
                    net = xml_nodes[0].getElementsByTagName("devices")[0].getElementsByTagName("interface")[0].getElementsByTagName("target")[0].getAttribute("dev")
                    net_stat = dom.interfaceStats(net)
                except Exception:
                    net_stat = [0,0,0,0,0,0,0,0,0,0,0,0,0]

                vms.append({'name': dom.name(),
                            'id': id,
                            'state': info[0],
                            'cpu_time': info[4],
                            'cpu_count': info[3],
                            'memory': info[2],
                            'rd_req': hdd_stat[0],
                            'rd_bytes': hdd_stat[1],
                            'wr_req': hdd_stat[2],
                            'wr_bytes': hdd_stat[3],
                            'rx_bytes': net_stat[0],
                            'rx_packets': net_stat[1],
                            'tx_bytes': net_stat[4],
                            'tx_packets': net_stat[5]
                            })
            except Exception, e:
                log.exception(0, 'libvirt lookup (%s id=%d): %s'%(hostname, id, str(e)))
                return None

        dom = None
        g = self.c.close()
        if g != 0:
            log.error(0, 'libvirt close error %s' % (str(g)))
        self.lv_data = [used_cpu, used_memory, total_cpu, total_memory, vms]
        return self.lv_data

    def kill(self):
        ok = True
        log.info(0, 'killing MonitorThread...')
        try:
            sys.exit()
        except Exception:
            log.info(0, 'monitorThread error...')
        log.info(0, 'MonitorThread killed')