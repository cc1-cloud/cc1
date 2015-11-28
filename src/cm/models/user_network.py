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

"""@package src.cm.views.user.network
@author Maciej Nabożny <mn@mnabozny.pl>


Database model describing user network
"""

from django.db import models

from cm.models.lease import Lease
from cm.utils.exception import CMException
from netaddr import IPNetwork


class UserNetwork(models.Model):
    address = models.CharField(max_length=20)
    mask = models.IntegerField()
    available_network = models.ForeignKey('AvailableNetwork')
    user = models.ForeignKey('User')
    name = models.CharField(max_length=200)

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return "%s/%d" % (self.address, self.mask)

    @property
    def dict(self):
        d = {}

        d['total_leases'] = self.lease_set.count()
        d['used_leases'] = d['total_leases'] - Lease.objects.filter(user_network=self).filter(vm=None).count()
        d['network_id'] = self.id
        d['address'] = self.address
        d['mask'] = self.mask
        d['available_network_id'] = self.available_network.id
        d['user_id'] = self.user.id
        d['name'] = self.name
        return d

    def to_cidr(self):
        return self.address + "/" + str(self.mask)

    def to_ipnetwork(self):
        return IPNetwork(self.address + "/" + str(self.mask))

    def is_in_use(self):
        for lease in self.lease_set.all():
            if lease.vm != None:
                return True
        return False

    def allocate(self):
        host_id = 0
        for host in self.to_ipnetwork().iter_hosts():
            host_id += 1
            # TODO: change it when using bridge networking model
            if host_id % 4 == 0:
                lease = Lease()
                lease.address = host
                lease.user_network = self
                lease.save()

    def release(self):
        """
        Remove all leases from this network
        """
        if self.is_in_use():
            raise CMException('network_in_use')

        for lease in self.lease_set.all():
            lease.delete()

    def get_unused(self):
        leases = filter(lambda x: x.vm == None, self.lease_set.all())
        if len(leases) == 0:
            raise CMException('lease_not_found')
        else:
            return leases[0]
