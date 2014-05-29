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

"""@package src.cm.models.node
"""

import socket

from django.db import models
from django.db.models import Sum

from cm.utils.exception import CMException
from common.states import node_states, vm_states  # , vnc_states,lease_states
import libvirt


class Node(models.Model):
    """
    @model{NODE} Class for Nodes in the cluster

    Node is physical machine providing its CPU for virtual machines ran
    within cluster. It hosts VMs with help of underlying Libvirt software.
    CM automatically selects node fitting best for newly created VM.
    User doesn't know which node it is exacly. He doesn't even need to be
    aware of nodes existence.

    VMs may start only on node with 'ok' state. CM automatically disables
    starting VMs on failed nodes.
    """
    username = models.CharField(max_length=30)
    address = models.CharField(max_length=45)
    transport = models.CharField(max_length=45)
    driver = models.CharField(max_length=45)
    suffix = models.CharField(max_length=20)
    cpu_total = models.IntegerField()
    memory_total = models.IntegerField()
    hdd_total = models.IntegerField()
    state = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'cm'

    # method for printing object instance
    def __unicode__(self):
        return str(self.id)

    @property
    def dict(self):
        """
        @returns{dict} node's data
        \n fields:
        @dictkey{id}
        @dictkey{address}
        @dictkey{cpu_total}
        @dictkey{cpu_free}
        @dictkey{memory_total}
        @dictkey{memory_free}
        @dictkey{hdd_total}
        @dictkey{hdd_free}
        @dictkey{state}
        """
        d = {}
        d['node_id'] = self.id
        d['address'] = self.address
        d['cpu_total'] = self.cpu_total
        d['cpu_free'] = self.cpu_free
        d['memory_total'] = self.memory_total
        d['memory_free'] = self.memory_free
        d['hdd_total'] = self.hdd_total
        d['hdd_free'] = self.hdd_free
        d['state'] = self.state
        d['comment'] = self.comment
        d['errors'] = self.errors or ''

        return d

    @property
    def long_dict(self):
        """
        @returns{dict} node's extended data
        \n fields:
        @dictkey{id}
        @dictkey{username}
        @dictkey{address}
        @dictkey{transport}
        @dictkey{driver}
        @dictkey{cpu_total}
        @dictkey{cpu_free}
        @dictkey{memory_total}
        @dictkey{memory_free}
        @dictkey{hdd_total}
        @dictkey{hdd_free}
        @dictkey{state}
        @dictkey{suffix}
        """
        d = {}
        d['node_id'] = self.id
        d['username'] = self.username
        d['address'] = self.address
        d['transport'] = self.transport
        d['driver'] = self.driver
        d['cpu_total'] = self.cpu_total
        d['cpu_free'] = self.cpu_free
        d['memory_total'] = self.memory_total
        d['memory_free'] = self.memory_free
        d['hdd_total'] = self.hdd_total
        d['hdd_free'] = self.hdd_free
        d['state'] = self.state
        d['suffix'] = self.suffix
        d['comment'] = self.comment
        d['errors'] = self.errors or ''

        return d

    @property
    def long_long_dict(self):
        """
        @returns{dict} node's further extended data
        \n fields:
        @dictkey{id}
        @dictkey{username}
        @dictkey{address}
        @dictkey{transport}
        @dictkey{driver}
        @dictkey{cpu_total}
        @dictkey{cpu_free}
        @dictkey{memory_total}
        @dictkey{memory_free}
        @dictkey{hdd_total}
        @dictkey{hdd_free}
        @dictkey{state}
        @dictkey{suffix}
        @dictkey{real_memory_total}
        @dictkey{real_memory_free}
        @dictkey{lv_memory_total}
        @dictkey{lv_memory_free}
        @dictkey{lv_cpu_total}
        @dictkey{lv_cpu_free}
        """
        d = {}
        d['node_id'] = self.id
        d['username'] = self.username
        d['address'] = self.address
        d['transport'] = self.transport
        d['driver'] = self.driver
        d['cpu_total'] = self.cpu_total
        d['cpu_free'] = self.cpu_free
        d['memory_total'] = self.memory_total
        d['memory_free'] = self.memory_free
        d['hdd_total'] = self.hdd_total
        d['hdd_free'] = self.hdd_free
        d['state'] = self.state
        d['suffix'] = self.suffix
        d['real_memory_total'] = self.real_memory_total
        d['real_memory_free'] = self.real_memory_free
        d['real_hdd_total'] = self.real_hdd_total
        d['real_hdd_free'] = self.real_hdd_free
        d['lv_memory_total'] = self.lv_memory_total
        d['lv_memory_free'] = self.lv_memory_free
        d['lv_cpu_total'] = self.lv_cpu_total
        d['lv_cpu_free'] = self.lv_cpu_free
        d['comment'] = self.comment
        d['errors'] = self.errors or ''

        return d

    @property
    def conn_string(self):
        """
        @returns{string} this Node's connection string
        """
        return '%s+%s://%s@%s%s' % (self.driver, self.transport, self.username, self.address, self.suffix)

    @property
    def ssh_string(self):
        """
        @returns{string} SSH address of this Node ('user\@address')
        """
        return '%s@%s' % (self.username, self.address)

    @property
    def cpu_free(self):
        """
        @returns{int} this Node's <b>free CPU</b> amount
        """

        c = self.vm_set.exclude(state__in=[vm_states['closed'], vm_states['erased']]).aggregate(cpu_sum=Sum('template__cpu'))
        csum = c['cpu_sum'] or 0  # 0 if no result exists in query

        c_free = self.cpu_total - csum

        return c_free

    @property
    def memory_free(self):
        """
        @returns{int} this Node's <b>free memory</b> amount
        """

        m = self.vm_set.exclude(state__in=[vm_states['closed'], vm_states['erased']]).aggregate(memory_sum=Sum('template__memory'))
        msum = m['memory_sum'] or 0  # 0 if no results exists in query

        m_free = self.memory_total - msum

        return m_free

    @property
    def hdd_free(self):
        """
        @returns{int} this Node's <b>free hdd</b> amount
        """

        s = self.vm_set.exclude(state__in=[vm_states['closed'], vm_states['erased']]).aggregate(size_sum=Sum('system_image__size'))
        ssum = s['size_sum'] or 0  # 0 if no results exists in query
        h_free = self.hdd_total - ssum

        return h_free

    # it connects through libvirt and read information for the node and put them in lv_data node attribute
    @property
    def read_lv_data(self):
        """
        @returns{array} resources data of this Node provided by Libvirt running on it:
        0. used_cpu,
        1. used_memory [KBytes],
        2. total_cpu,
        3. total_memory [MBytes],
        4. free_memory [Bytes],
        5. pool_total_space [Bytes],
        6. pool_free_space [Bytes]
        """
        if hasattr(self, 'lv_data'):
            return self.lv_data

        conn = libvirt.open(self.conn_string)
        used_cpu = 0
        used_memory = 0
        total_cpu = conn.getInfo()[2]
        total_memory = conn.getInfo()[1]  # MBytes
        free_memory = conn.getFreeMemory()  # Bytes

        pool = conn.storagePoolLookupByName('images')
        pool.refresh(0)
        pool_total_space = pool.info()[1]  # Bytes
        pool_free_space = pool.info()[3]  # Bytes
        for id_dom in conn.listDomainsID():
            dom = conn.lookupByID(id_dom)
            info = dom.info()  # struct virDomainInfo
            used_cpu += info[3]
            used_memory += info[1]  # KBytes
        self.lv_data = [used_cpu, used_memory, total_cpu, total_memory, free_memory, pool_total_space, pool_free_space]
        conn.close()
        return self.lv_data

    @property
    def lv_memory_total(self):
        """
        @returns{int} this Node's <b>total memory</b> amount [MB] (according to Libvirt)
        """
        return self.read_lv_data[3]

    @property
    def lv_memory_free(self):
        """
        @returns{int} this Node's <b>free memory</b> amount [MB] (according to libvirt)
        """
        r = self.read_lv_data[3] - self.read_lv_data[1] / 1024
        return r

    @property
    def lv_cpu_total(self):
        """
        @returns{int} this Node's <b>total CPU</b> amount (according to libvirt)
        """
        return self.read_lv_data[2]

    @property
    def lv_cpu_free(self):
        """
        @returns{int} this Node's <b>free CPU</b> amount (according to libvirt)
        """
        r = self.read_lv_data[2] - self.read_lv_data[0]
        return r

    @property
    def real_memory_total(self):
        """
        @returns{int} this Node's <b>total memory</b> amount [MB] (real)
        """
        return self.read_lv_data[3]

    @property
    def real_memory_free(self):
        """
        @returns{int} this Node's <b>free memory</b> amount [MB] (real)
        """
        r = self.read_lv_data[4] / 1024 / 1024
        return r

    @property
    def real_hdd_total(self):
        """
        @returns{int} this Node's <b>total HDD</b> storage amount [MB] (real)
        """
        r = self.read_lv_data[5] / 1024 / 1024
        return r

    @property
    def real_hdd_free(self):
        """
        @returns{int} this Node's <b>free HDD</b> amount [MB] (real)
        """
        r = self.read_lv_data[6] / 1024 / 1024
        return r

    @property
    def get_cm_ip(self):
        """
        Method
        """
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            conn.connect(('192.245.169.43', 22))
        except:
            raise CMException('node_connect')
        ip = conn.getsockname()[0]
        conn.close()

        return ip

    @staticmethod
    def get(user_id, node_id):
        """
        @parameter{user_id,int} id of the declared Node's owner
        @parameter{node_id,int} requested Node's id

        @returns{Node} instance of the requested Node

        @raises{node_get,CMException} no such Node
        """

        # entities.user.User.superuser(user_id)

        # check on auth is performed by decorator
        # Admin.superuser(user_id)

        try:
            n = Node.objects.get(pk=node_id)
        except:
            raise CMException('node_get')

        return n

    # sets node's stat to locked
    def lock(self):
        """
        Method sets node's stat to locked.
        """
        self.state = node_states['locked']
        self.save()
        # TODO: send imejl

    # the funcion is called by vm utils create
    # finds first node (or with node_id, if given) that is sufficient enough for image and template and returns it.
    @staticmethod
    def get_free_node(template, image, node_id=None):
        """
        Method finds first (or with given id) Node that is sufficient enough
        for specified \c Image and \c Template and returns that Node.

        @parameter{template,Template} instance of the VM's Template to run on
        searched Node
        @parameter{image,Image} instance of the Image to run on searched Node
        @parameter{node_id,int} @optional{first suitable}

        @returns{Node} sufficient instance of the Node

        @raises{node_get,CMException} cannot get sufficient Node
        """
        if node_id:
            node = Node.objects.get(pk=node_id)
            if node.cpu_free >= template.cpu and node.memory_free >= template.memory and node.hdd_free >= image.size:
                return node
            else:
                raise CMException('node_get')
        else:
            available_nodes = []

            # Get all nodes, which fit this VM
            for node in Node.objects.filter(state__exact=node_states['ok']):
                if node.cpu_free >= template.cpu and node.memory_free >= template.memory and node.hdd_free >= image.size:
                    available_nodes.append(node)

            if not available_nodes:
                raise CMException('node_get')

            # Get best matching (most filled) node
            available_nodes.sort(key=lambda node: node.cpu_free)
            return available_nodes[0]

    # TODO:
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # define: get_lease(), get_vnc()
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
