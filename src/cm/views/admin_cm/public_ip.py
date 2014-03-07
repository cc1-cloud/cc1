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


Functions to manage public leases in database for CM Administrator
"""

from netaddr.ip import IPAddress
from cm.models.public_ip import PublicIP
from cm.utils import log
from cm.utils.exception import CMException
from cm.utils.decorators import admin_cm_log
from cm.models.lease import Lease

import netaddr


@admin_cm_log(log=True)
def get_list(caller_id):
    leases = PublicIP.objects.all()
    return [lease.dict for lease in leases]


@admin_cm_log(log=True)
def add(caller_id, start_address, count):
    ips = [ip.address for ip in PublicIP.objects.all()]

    pool = netaddr.IPAddress(start_address)
    for i in xrange(count):
        if str(pool+i) in ips:
            log.debug(caller_id, 'Ip %s is a duplicate! Skipping' % str(pool+i))
        elif not IPAddress(pool+1).is_unicast():
            log.debug(caller_id, 'Ip %s is not an unicast address! Skipping' % str(pool+i))
        else:
            log.debug(caller_id, 'Adding public ip %s' % str(pool+i))
            public_lease = PublicIP()
            public_lease.address = str(pool + i)
            public_lease.save()


@admin_cm_log(log=True)
def delete(caller_id, public_ip_id_list):
    for ip_address in public_ip_id_list:
        lease = PublicIP.objects.get(id=ip_address)
        if lease.lease != None:
            raise CMException('lease_in_use')


    for ip_address in public_ip_id_list:
        lease = PublicIP.objects.get(id=ip_address)
        lease.delete()


@admin_cm_log(log=True)
def unassign(caller_id, lease_id):
    """
    Method detaches public IP from caller's VM.
    Unlinks PublicLease instance from given VM's Lease instance.
    @decoratedby{src.cm.utils.decorators.user_log}

    @parameter{lease_id,int} id of the VM's lease from which IP should be detached.

    @response{None}

    @raises{lease_not_found,CMException}
    @raises{public_lease_unassign,CMException}
    """

    try:
        lease = Lease.objects.get(id=lease_id)
    except Exception, e:
        log.exception(caller_id, str(e))
        raise CMException("lease_not_found")

    if lease.vm == None:
        raise CMException('lease_not_assigned')

    try:
        public_ip = lease.publicip_set.all()[0]
    except:
        raise CMException('public_lease_assigned')

    public_ip.unassign()
    public_ip.save()
