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

"""@package src.cm.views.suer.network
@author Maciej Nabożny <mn@mnabozny.pl>


Database model describing single lease or mirco-network (depends on networking
model) for VM
"""
from django.db import models
from django.template import loader, Context
from netaddr import IPNetwork, IPAddress

import socket
import libvirt

from cm.utils.exception import CMException
from cm.utils import log
from cm.settings import DNS_DOMAIN

class Lease(models.Model):
    address = models.CharField(max_length=20)
    user_network = models.ForeignKey('UserNetwork')
    vm = models.ForeignKey('VM', null=True, blank=True)

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return self.address

    @property
    def dict(self):
        d = {}
        d['lease_id'] = self.id
        d['address'] = self.vm_address
        d['user_network_id'] = self.user_network.id
        if self.vm:
            d['vm'] = self.vm.id
        else:
            d['vm'] = None
        d['user_id'] = self.user_network.user.id
        try:
            d['public_ip'] = self.publicip_set.all()[0].dict
        except:
            d['public_ip'] = ''

        return d

    @property
    def node_address(self):
        network = IPNetwork('%s/30' % self.address)
        return str(network.network + 1)

    @property
    def vm_address(self):
        network = IPNetwork('%s/30' % self.address)
        return str(network.network + 2)

    @property
    def cm_address(self):
        if self.vm == None or self.vm.node == None:
            raise CMException('lease_not_attached')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.vm.node.address, 22))
        return s.getsockname()[0]

    @property
    def domain_name(self):
        return DNS_DOMAIN

    @property
    def hostname(self):
        return 'vm-%d' % self.vm.id

    @property
    def mac(self):
        ip_hex = '%08x' % IPAddress(self.address).value
        return '00:02:%s:%s:%s:%s' % (ip_hex[0:2], ip_hex[2:4], ip_hex[4:6], ip_hex[6:8])

    def attach_node(self):
        template = loader.get_template('networking/routed.xml')
        context = Context({
            'lease': self,
            'vm': self.vm
        })

        network_xml = template.render(context)
        log.debug(self.user_network.user.id, "Rendered network template:\n%s" % network_xml)
        conn = libvirt.open(self.vm.node.conn_string)
        net = conn.networkDefineXML(network_xml)
        net.create()

    def detach_node(self):
        """
        @raises{lease_detached,CMException} Network was not defined
        """
        if self.vm_id == None:
            raise CMException('lease_detached')

        # Destroy network
        try:
            conn = libvirt.open(self.vm.node.conn_string)
        except Exception, e:
            log.exception(self.user_network.user_id, "Cannot connet to libvirt: ")
            raise CMException('lease_detach')

        lv_network = None
        try:
            lv_network = conn.networkLookupByName('net-%d-%d' % (self.vm.id, self.id))
        except Exception, e:  # it's sad that network is missing, but if it was WN from init_head state farm, it's ok
            log.error(self.user_network.user_id, "Cannotfind libvirt network: %s" % str(e))
            lv_network = None

        if lv_network:
            try:
                lv_network.destroy()
                lv_network.undefine()
            except Exception, e:  # it's sad that network is missing, but if it was WN from init_head state farm, it's ok
                log.error(self.user_network.user_id, "Cannot destroy or undefine libvirt network: %s" % str(e))

        # Detach public ip
        for public_lease in self.publicip_set.all():
            log.debug(self.user_network.user.id, "\t...detaching public lease %s" % public_lease.address)
            public_lease.unassign()

        conn.close()
        self.vm_id = None
        self.save()
