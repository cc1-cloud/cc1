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

"""@package src.cm.manager.contextualization.user

@alldecoratedby{src.cm.utils.decorators.user_log}
"""
from cm.models.command import Command
from cm.utils.decorators import user_log


@user_log(log=True)
def shutdown(caller_id, vm_id, timeout='now'):
    """
    Method executes \c shutdown on virtual machines listed in \c vm_list
    at given \c timeout (*now* by default) provided they belong to caller.
    @decoratedby{src.cm.utils.decorators.user_log}

    @parameter{vm_id,int}
    @parameter{timeout,string} optional, "now" by default
    """
    return Command.execute('shutdown', caller_id, vm_id, timeout=timeout)


@user_log(log=True)
def reboot(caller_id, vm_id, timeout='now'):
    """
    Function executes \c reboot on given VM at given \c timeout (*now* by default).
    @warning Deprecated since execution's success/failure depends on inner
    VM's state.
    @decoratedby{src.cm.utils.decorators.user_log}

    @parameter{vm_id,int} id of the VM to reboot
    @parameter{timeout,string} @optional{"now"}
    """
    return Command.execute('reboot', caller_id, vm_id, timeout=timeout)


@user_log(log=True)
def reset_password(caller_id, vm_id, vm_username):
    """
    Method resets password of the existing OS user \c user_name on given VM.
    @decoratedby{src.cm.utils.decorators.user_log}

    @parameter{vm_id,int}
    @parameter{data,dict}
    \n fields:
    @dictkey{user_name,string} whose password is to be reseted
    @dictkey{password,string} new password to set

    @noresponse
    """
    return {'password': Command.execute('reset_password', caller_id, vm_id, user=vm_username)}


@user_log(log=True)
def add_ssh_key(caller_id, vm_ids, vm_username, vm_key):
    """
    Method sets key \c vm_key on each machine listed in \c vm_ids
    (provided they belong to caller).
    @decoratedby{src.cm.utils.decorators.user_log}

    @parameter{vm_ids,int} id's of the VMs to add SSH key on which
    @parameter{data,dict}
    \n fields:
    @dictkey{vm_username,string}
    @dictkey{vm_key,string}
    """
    results = ''
    for vm_id in vm_ids:
        results += Command.execute('add_ssh_key', caller_id, vm_id, user=vm_username, ssh_key=vm_key)
    return results
