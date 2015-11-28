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

"""@package src.cm.views.ci.public_ip
@author Maciej Nabozny <mn@mnabozny.pl>
@alldecoratedby{src.cm.utils.decorators.ni_log}
"""

from cm.utils.decorators import ci_log
from cm.models.node import Node
from cm.utils import log
from cm.utils.exception import CMException
from common.states import vm_states


@ci_log(log=True)
def get_list(remote_ip):
    """
    @cmview_ci
    @param_post{remote_ip,string}
    """
    try:
        node = Node.objects.get(address=remote_ip)
    except:
        log.error(0, 'Cannot find node: %s' % remote_ip)
        raise CMException('node_not_found')

    vms = node.vm_set.filter(state__in=[vm_states['running'], vm_states['running ctx'], vm_states['init']]).all()
    public_leases = []
    for vm in vms:
        for lease in vm.lease_set.all():
            if lease.publicip_set.count() != 0:
                d = {}
                d['vm_id'] = vm.id
                d['private_lease'] = lease.vm_address
                d['public_lease'] = lease.publicip_set.all()[0].address
                public_leases.append(d)
    return public_leases
