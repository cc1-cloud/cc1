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

"""@package src.cm.models.available_netword
@author Maciej Nabożny <mn@mnabozny.pl>

Database model describing ip pool for user netwroks
"""

import traceback

from django.db import models

from cm.models.user_network import UserNetwork
from cm.utils import log
from cm.utils.exception import CMException
from common.states import available_network_states
from netaddr import IPNetwork


class AvailableNetwork(models.Model):
    address = models.CharField(max_length=20)
    mask = models.IntegerField()
    state = models.IntegerField()

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return "%s/%d" % (self.address, self.mask)

    @property
    def dict(self):
        d = {}
        d['pool_id'] = self.id
        d['address'] = self.address
        d['mask'] = self.mask
        d['state'] = self.state
        return d

    def to_cidr(self):
        return self.address + "/" + str(self.mask)

    def to_ipnetwork(self):
        return IPNetwork(self.address + "/" + str(self.mask))

    def is_in_use(self):
        """
        Check if any vm uses this network
        """
        for net in self.usernetwork_set.all():
            if net.is_in_use():
                return True
        return False

    def release(self):
        """
        Removes all user networks from this network
        """
        if self.is_in_use():
            raise CMException('network_in_use')

        for net in self.usernetwork_set.all():
            net.release()
            net.delete()

    def get_unused_ipnetwork(self, mask):
        """
        @returns Unused subnetwork represented by IPNetwork object
        """
        networks = []
        for network in self.usernetwork_set.all():
            networks.append(network.to_ipnetwork())
        networks = sorted(networks)

        log.debug(1, 'Networks: %s' % str(networks))

        if self.mask > mask:
            raise CMException('network_to_large')

        if len(networks) == 0:
            return IPNetwork(self.address + '/' + str(mask))

        if IPNetwork(self.address + '/' + str(mask)).network < networks[0].network:
            return IPNetwork(self.address + '/' + str(mask))

        # Find matching hole in existing networks
        for i in xrange(len(networks) - 1):
            n = IPNetwork(str(networks[i].next().ip) + "/" + str(mask))
            if networks[i] < n and n < networks[i + 1]:
                return n

        # If previous fails, try to fit network at end of pool
        n = IPNetwork(str(networks[-1].next().network) + "/" + str(mask))
        log.debug(1, 'Trying: %s' % str(n))
        if networks[-1].network < n.network and n.network < self.to_ipnetwork().next().network:
            return n
        else:
            # or raise exception, if this is not possible
            raise CMException("network_unavailable")

    @staticmethod
    def get_lease(user):
        """
        Get unused lease for given user and vm
        """
        user_networks = UserNetwork.objects.filter(user=user).all()
        lease = None

        for network in user_networks:
            try:
                lease = network.get_unused()
                break
            except:
                log.debug(user.id, 'UserNetwork %s has no leases' % str(network.address))

        if lease == None:
            log.debug(user.id, 'No lease found in existing networks. Allocating new UserNetwork')
            for pool in AvailableNetwork.objects.filter(state=available_network_states['ok']):
                try:
                    ipnet = pool.get_unused_ipnetwork(26)

                    log.debug(user.id, 'Allocated new user_network: %s' % str(ipnet))
                    network = UserNetwork()
                    network.user = user
                    network.mask = ipnet.prefixlen
                    network.address = str(ipnet.network)
                    network.name = "Auto-generated network"
                    network.available_network = pool

                    network.save()
                    network.allocate()

                    lease = network.get_unused()
                    break
                except Exception, e:
                    f = open('/tmp/trace', 'a')
                    traceback.print_exc(file=f)
                    f.close()
                    log.debug(user.id, "Cannot allocate new network in %s: %s" % (str(pool.address), str(e)))

        if lease == None:
            raise CMException('available_network_not_found')
        else:
            return lease
