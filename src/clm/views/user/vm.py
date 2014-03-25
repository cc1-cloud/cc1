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

"""@package src.clm.views.user.vm
@alldecoratedby{src.clm.utils.decorators.user_log}
@author Maciej Nabożny <di.dijo@gmail.com>
"""

from clm.models.user import User
from clm.utils.decorators import user_log, cm_request
from clm.utils.cm import CM
from common.states import group_states


@user_log(log=True, pack=False)
def create(cm_id, caller_id, **data):
    """
    @parameter{machine,dict}
    \n fields @asrequired{src.cm.element.role.action} except for \c groups.
    """
    user = User.get(caller_id)
    groups = list(user.group_set.filter(usergroup__status__exact=group_states['ok']).values_list('id', flat=True))
    return CM(cm_id).send_request("user/vm/create/", caller_id=caller_id, groups=groups, **data)


@user_log(log=True, pack=False)
@cm_request
def destroy(cm_response, **data):
    """
    @parameter{id} list of id's of the machines to destroy
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):  # @todo rename for fun name consistency
    """
    @parameter{id,int} id of the vm to get
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def save_and_shutdown(cm_response, **data):
    """
    @parameter{vmid,int} id of the VM to save
    @parameter{data,dict}
    \n fields @asrequired{src.cm.views.utils.image.save_and_shutdown()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def reset(cm_response, **data):
    """
    @parameter{vmid,int} list of the ids of the VMs to reset
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def edit(cm_response, **data):
    """
    @parameter{vm_id,int}
    @parameter{data,dict}
    \n fields:
    @dictkey{name,string}
    @dictkey{description,string}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def attach_vnc(cm_response, **data):
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def detach_vnc(cm_response, **data):
    return cm_response
