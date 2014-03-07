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

from clm.utils.decorators import user_log, cm_request
from clm.models.key import Key
from clm.utils.exception import CLMException
from clm.utils.cm import CM


@user_log(log=True, pack=False)
@cm_request
def shutdown(cm_response, **data):
    """
    @clmview_user
    @clm_view_transparent{user.ctx.shutdown()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def reboot(cm_response, **data):
    """
    @clmview_user
    @clm_view_transparent{user.ctx.reboot()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def reset_password(cm_response, **data):
    """
    @clmview_user
    @clm_view_transparent{user.ctx.reset_password()}
    """
    return cm_response


@user_log(log=True, pack=False)
def add_ssh_key(cm_id, caller_id, vm_key, vm_username, vm_ids):
    """
    @clmview_user
    @clm_view_transparent{user.ctx.add_ssh_key()}
    """
    try:
        k = Key.objects.filter(user_id__exact=caller_id).filter(id__exact=vm_key)[0]
    except:
        raise CLMException('ssh_key_get')

    return CM(cm_id).send_request("user/ctx/add_ssh_key/", caller_id=caller_id, vm_username=vm_username, vm_ids=vm_ids, vm_key=k.dict['data'])
