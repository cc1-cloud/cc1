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

"""@package src.cm.views.ci.vm

@author Maciej Nabozny <mn@mnabozny.pl>
@alldecoratedby{src.cm.utils.decorators.user_log}
"""

import libvirt

from common import log
from common.states import vm_states

from cm.utils.decorators import ci_log
from cm.utils.exception import CMException
from cm.utils.threads.vm import VMThread
from cm.models.vm import VM
from cm.models.node import Node


@ci_log(log=True)
def update_state(remote_ip, vm_name, action, state):
    """
    @cmview_ci
    @param_post{remote_ip,string}
    @param_post{vm_name}
    @param_post{action}
    @param_post{state}
    """
    try:
        node = Node.objects.get(address=remote_ip)
    except:
        raise CMException('node_not_found')

    try:
        vm_id = int(vm_name.split('-')[1])
        user_id = int(vm_name.split('-')[2])
    except:
        log.debug(0, "Unknown vm from hook: %s" % vm_name)
        raise CMException('vm_not_found')

    if action != "stopped":
        log.debug(user_id, "Not updating vm state: action is %s" % str(action))
        return ''

    try:
        VM.objects.update()
        vm = VM.objects.get(id=vm_id)
    except:
        log.error(user_id, 'Cannot find vm in database!')
        raise CMException('vm_not_found')

    if not vm.state in [vm_states['running ctx'], vm_states['running']]:
        log.error(user_id, 'VM is not running!')
        raise CMException('vm_not_running')

    if vm.state == vm_states['restart']:
        raise CMException('vm_restart')

    thread = VMThread(vm, 'delete')
    thread.start()

    return ''
