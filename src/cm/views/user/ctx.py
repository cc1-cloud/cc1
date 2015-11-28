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

"""@package src.cm.views.user.ctx

@alldecoratedby{src.cm.utils.decorators.user_log}
"""
from cm.models.command import Command
from cm.utils.decorators import user_log


@user_log(log=True)
def shutdown(caller_id, vm_id, timeout='now'):
    """
    Executes \c shutdown on virtual machines listed in \c vm_list at a given
    \c timeout (@val{now} by default) provided they belong to caller.

    @cmview_user
    @param_post{vm_id,int}
    @param_post{timeout,string} optional, "now" by default
    """
    return Command.execute('shutdown', caller_id, vm_id, timeout=timeout)


@user_log(log=True)
def reboot(caller_id, vm_id, timeout='now'):
    """
    Executes reboot on given VM at given timeout. Be default it's executed
    with no delay.

    @warning Deprecated since execution's success/failure depends on inner
    VM's state.

    @cmview_user
    @param_post{vm_id,int} id of the VM to reboot
    @param_post{timeout,string} @optional{"now"}
    """
    return Command.execute('reboot', caller_id, vm_id, timeout=timeout)


@user_log(log=True)
def reset_password(caller_id, vm_id, vm_username):
    """
    Resets password of the existing OS user \c user_name on given VM. User
    obtains new randomly created password. Such a password is sent in CM
    response. It is recommended to change password manually afterwards.

    @cmview_user
    @param_post{vm_id,int}
    @param_post{vm_username,string} username of the user whose password should
    be reseted
    """
    return {'password': Command.execute('reset_password', caller_id, vm_id, user=vm_username)}


@user_log(log=True)
def add_ssh_key(caller_id, vm_ids, vm_username, vm_key):
    """
    Injects given SSH public key to authorized keys on specified VMs.

    @cmview_user
    @param_post{vm_ids,list(int)} id's of the VMs where SSH public key should be injected
    @param_post{vm_username,string}
    @param_post{vm_key,string}
    """
    results = ''
    for vm_id in vm_ids:
        results += Command.execute('add_ssh_key', caller_id, vm_id, user=vm_username, ssh_key=vm_key)
    return results
