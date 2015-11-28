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

"""@package src.clm.views.admin_cm.vm
@alldecoratedby{src.clm.utils.decorators.admin_cm_log}
@author Maciej Nabożny <mn@mnabozny.pl>
"""

from clm.models.user import User
from clm.utils.cm import CM
from clm.utils.decorators import admin_cm_log, cm_request
from clm.utils.exception import CLMException


@admin_cm_log(log=True, pack=False)
@cm_request
def create(cm_response, **data):
    """
    Creates nev VM

    @clmview_admin_cm
    @cm_request_transparent{vm.create()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def destroy(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{vm.destroy()}
    """
    return cm_response


@admin_cm_log(log=False)
def get_list(cm_id, caller_id, cm_password, user_id):
    """
    @clmview_admin_cm
    @cm_request{storage_image.get_list()}
    @param_post{user_id,int}
    """

    names = {}
    resp = CM(cm_id).send_request("admin_cm/vm/get_list/", caller_id=caller_id, cm_password=cm_password, user_id=user_id)

    for vm in resp['data']:
        if str(vm['user_id']) not in names:
            try:
                user = User.objects.get(pk=vm['user_id'])
                names[str(vm['user_id'])] = user.first + " " + user.last
            except:
                raise CLMException('user_get')
        vm['owner'] = names[str(vm['user_id'])]

    return resp['data']


@admin_cm_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{vm.get_by_id()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def save_and_shutdown(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{vm.save_and_shutdown()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def restart(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{vm.restart()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def erase(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{vm.erase()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def attach_vnc(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{vm.attach_vnc()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def detach_vnc(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{vm.detach_vnc()}
    """
    return cm_response
