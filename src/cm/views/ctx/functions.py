# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @COPYRIGHT_end

"""@package src.cm.manager.contextualization.rest_service
"""
from cm.utils.decorators import ctx_log
from cm.utils import log
from actions import VERSION
import os
import json
from common.states import command_states
from common import response
from cm.models.vm import VM
from cm.models.command import Command


@ctx_log(log=True)
def hello(remote_ip, **kw):
    """
    REST stub for hello function

    @parameter{kw}
    @returns HTTP response
    """
    vm = VM.get_by_ip(remote_ip)
    log.info(vm.user_id, "vm  called hello")
    Command.hello(remote_ip)

    r = response('ok')
    if int(kw.get('version', 0)) < VERSION:
        f = file(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'actions.py'), 'r')
        r['actions_file'] = f.read()
        f.close()
    return r

@ctx_log(log=True)
def get_command(remote_ip, **kw):
    """
    @parameter{kw}
    @returns{Command} next command from the que to the asking VM
    """
    vm = VM.get_by_ip(remote_ip)

    log.debug(0, "Get first command for %s" % vm.id)
    command = vm.command_set.filter(state=command_states['pending']).order_by('id')
    if len(command) == 0:
        return response('ctx_no_command')

    command = command[0]

    log.debug(0, "First command is %s" % command.id)
    command.state = command_states['executing']
    command.save()

    d = command.dict()

    r = response('ok', d)
    if int(kw.get('version', 0)) < VERSION:
        f = file(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'actions.py'), 'r')
        r['actions_file'] = f.read()
        f.close()
    return r

@ctx_log(log=True)
def finish_command(remote_ip, command_id, status, returns=None, **kw):
    """
    REST stub for finish_command

    @parameter{command_id,string} hash string identyfing command
    @parameter{status,string}
    @parameter{returns,dict} dictionary containing VM returned values
    """
    vm = VM.get_by_ip(remote_ip)

    if returns:
        returns = json.dumps(returns)

    log.debug(0, "Select command %s %s" % (command_id, status))
    try:
        command = vm.command_set.get(id=command_id)
    except Command.DoesNotExist:
        return

    log.debug(0, "Finish command %s" % command)
    if command is None:
        for c in Command.objects.all():
            log.debug(0, 'Finish - Available cmds id:%s,  state:%s, name:%s, vmid:%s' % (c.id, c.state, c.name, c.vm_id))
        return
    log.debug(vm.user_id, "command state %s" % command.state)

    command.response = returns
    command.state = command_states[status]
    log.debug(vm.user_id, "Finish command %s" % command.id)
    command.save()

    r = response('ok')
    if int(kw.get('version', 0)) < VERSION:
        f = file(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'actions.py'), 'r')
        r['actions_file'] = f.read()
        f.close()
    return r
