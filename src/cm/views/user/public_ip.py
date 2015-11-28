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

"""@package src.cm.views.user.public_ip

@alldecoratedby{src.cm.utils.decorators.user_log}
@author Maciej Nabożny <di.dijo@gmail.com>
@author Tomasz Sośnicki <tom.sosnicki@gmail.com>
"""

from cm.models.lease import Lease
from cm.utils.exception import CMException
from cm.utils import log
from cm.models.user import User
from cm.models.public_ip import PublicIP
from cm.utils.decorators import user_log
from datetime import datetime


@user_log(log=True)
def get_list(caller_id):
    """
    @cmview_user
    @response{list(dict)} PublicIP.dict property for each caller's PublicIP
    """
    user = User.get(caller_id)

    ips = PublicIP.objects.filter(user=user).all()
    return [ip.dict for ip in ips]


@user_log(log=True)
def request(caller_id):
    """
    Method requests single PublicIP address for caller. If caller's quota
    is exceeded, exception is raised. Otherwise caller obtains a new PublicIP
    address.

    @cmview_user
    @response{string} newly obtained PublicIP's address

    @raises{public_lease_not_found,CMException}
    @raises{public_lease_request,CMException}
    """
    user = User.get(caller_id)

    if len(user.public_ips.all()) >= user.public_ip:
        raise CMException('public_lease_limit')

    ips = PublicIP.objects.filter(user=None).all()
    if len(ips) == 0:
        raise CMException('public_lease_not_found')

    ip = ips[0]
    ip.user = user
    ip.request_time = datetime.now()
    ip.release_time = None
    try:
        ip.save()
    except Exception:
        raise CMException('public_lease_request')
    return ip.address


@user_log(log=True)
def assign(caller_id, lease_id, public_ip_id):
    """
    Method attaches caller's PublicIP to his VM. VM's Lease instance's is
    assigned to PublicIP.

    @cmview_user
    @param_post{lease_id} id of the Lease in caller's UserNetwork
    @param_post{public_ip_id} id of the Public_IP to be attached to VM

    @raises{lease_not_found,CMException}
    @raises{lease_not_assigned,CMException}
    @raises{public_lease_assign,CMException}
    """
    user = User.get(caller_id)

    try:
        lease = Lease.objects.filter(user_network__user=user).get(id=lease_id)
        public_ip = PublicIP.objects.filter(user=user).get(id=public_ip_id)
    except Exception, e:
        log.exception(caller_id, str(e))
        raise CMException("lease_not_found")

    if lease.vm == None:
        raise CMException('lease_not_assigned')

    if public_ip.lease != None:
        raise CMException('public_lease_assigned')

    public_ip.assign(lease)
    public_ip.save()


@user_log(log=True)
def unassign(caller_id, lease_id):
    """
    Method detaches PublicIP from caller's VM.

    @cmview_user
    @param_post{lease_id,int} id of the VM's Lease from which PublicIP should
    be detached.

    @raises{lease_not_found,CMException}
    @raises{public_lease_unassign,CMException}
    """
    user = User.get(caller_id)

    try:
        lease = Lease.objects.get(id=lease_id)
    except Exception, e:
        log.exception(caller_id, str(e))
        raise CMException("lease_not_found")

    if lease.user_network.user != user:
        raise CMException("lease_not_found")

    if lease.vm == None:
        raise CMException('lease_not_assigned')

    try:
        public_ip = lease.publicip_set.all()[0]
    except:
        raise CMException('public_lease_assigned')

    public_ip.unassign()
    public_ip.save()


@user_log(log=True)
def release(caller_id, public_ip_id):
    """
    Removes PublicIP from caller's pool and returns it to publicly available
    pool, provided PublicIP isn't in use.

    @note There's very low probability of obtaining the same PublicIP address
    once again.

    @cmview_user
    @param_post{public_ip_id,int} id of the PublicIP to release
    """
    user = User.get(caller_id)
    public_lease = PublicIP.objects.filter(user=user).get(id=public_ip_id)

    if public_lease.lease:
        raise CMException('public_lease_assigned')

    public_lease.user = None
    public_lease.save()
