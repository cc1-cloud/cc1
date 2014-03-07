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


Database model describing public ip addresses, which could be mapped on vm ip
lease (Lease entity). Attached ips are redirected by nodes, on which vm are
running. This is done by one-to-one NAT (SNAT+DNAT)
"""

import subprocess

from django.db import models

from cm.utils import log
from cm.utils.exception import CMException


class PublicIP(models.Model):
    address = models.IPAddressField()
    lease = models.ForeignKey('Lease', blank=True, null=True)
    user = models.ForeignKey('User', blank=True, null=True, related_name='public_ips')

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return self.address

    @property
    def dict(self):
        """
        @returns{dict} this PublicLease's data
        \n fields:
        @dictkey{id,int} this PublicLease's id
        @dictkey{ip,string} IP address corresponding to this PublicLease
        @dictkey{lease_id,int} id of the wrapped Lease
        @dictkey{vm_name,string} VM, to which IP is attached
        @dictkey{user_id,int} owner, if there is any
        """
        d = {}
        d['ip_id'] = self.id
        d['public_ip_id'] = self.id
        d['address'] = self.address
        if self.lease:
            d['lease_id'] = self.lease.id
            if self.lease.vm:
                d['vm_name'] = self.lease.vm.name if self.lease and self.lease.vm else ''
            else:
                d['vm_name'] = ''
        else:
            d['lease_id'] = ''
            d['vm_name'] = ''

        if self.user:
            d['user_id'] = self.user.id
        else:
            d['user_id'] = ''
        return d

    @property
    def mac(self):
        # TODO where we use it?
        return ''

    def assign(self, lease):
        if lease.vm == None:
            raise CMException('lease_not_attached')

        self.lease = lease
        self.save()

        log.debug(0, "Attaching ip with comand: %s" % str(['ssh',
                                                           '-i',
                                                           '/var/lib/cc1/.ssh/id_rsa',
                                                           '%s@%s' % (lease.vm.node.username, lease.vm.node.address),
                                                           'sudo /usr/sbin/cc1_node_public_ip attach %d %s %s' % (lease.vm.id, lease.vm_address, self.address)]))

        p = subprocess.Popen(['ssh',
                              '-i',
                              '/var/lib/cc1/.ssh/id_rsa',
                              '%s@%s' % (lease.vm.node.username, lease.vm.node.address),
                              'sudo /usr/sbin/cc1_node_public_ip attach %d %s %s' % (lease.vm.id, lease.vm_address, self.address)],
                             stdout=subprocess.PIPE)
        p.wait()
        log.debug(self.user.id, p.stdout.read())

        if p.returncode != 0:
            log.error(self.user.id, "SSH error: %d" % p.returncode)
            raise CMException('public_ip_failed')

    def unassign(self):
        if self.lease == None:
            raise CMException('public_ip_not_attached')

        if self.lease.vm == None:
            raise CMException('lease_not_attached')

        log.debug(0, "Detaching ip with comand: %s" % str(['ssh',
                                                          '-i',
                                                          '/var/lib/cc1/.ssh/id_rsa',
                                                          '%s@%s' % (self.lease.vm.node.username, self.lease.vm.node.address),
                                                          'sudo /usr/sbin/cc1_node_public_ip detach %d %s %s' % (self.lease.vm.id, self.lease.vm_address, self.address)]))
        p = subprocess.Popen(['ssh',
                              '-i',
                              '/var/lib/cc1/.ssh/id_rsa',
                              '%s@%s' % (self.lease.vm.node.username, self.lease.vm.node.address),
                              'sudo /usr/sbin/cc1_node_public_ip detach %d %s %s' % (self.lease.vm.id, self.lease.vm_address, self.address)],
                             stdout=subprocess.PIPE)
        p.wait()
        log.debug(self.user.id, p.stdout.read())

        self.lease = None
        self.save()

        if p.returncode != 0:
            raise CMException('public_ip_failed')
