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

"""@package src.clm.views.admin_cm.admin
@alldecoratedby{src.clm.utils.decorators.admin_cm_log}
"""
from clm.models.cluster import Cluster
from clm.models.user import User
from clm.utils.cm import CM
from clm.utils.decorators import admin_cm_log, cm_request
from clm.utils.exception import CLMException


@admin_cm_log(log=True, pack=False)
@cm_request
def add(cm_response, **data):
    """
    @clmview_admin_clm
    @cm_request_transparent{admin.add()}
    """
    if cm_response['status'] == 'ok':
        try:
            user = User.get(data['user_id'])
            user.is_superuser_cm = 1
            user.save()
        except:
            CLMException('cm_admin_add')

    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @clmview_admin_clm
    @cm_request_transparent{admin.delete()}
    """
    is_admin = False
    for cm_id in [cluster.id for cluster in Cluster.objects.all()]:
        resp = CM(cm_id).send_request('admin_cm/admin/am_i_admin/', caller_id=data['user_id'])
        if resp['status'] == 'ok' and resp['data']:
            is_admin = True
            break
    if not is_admin:
        try:
            user = User.get(data['user_id'])
            user.is_superuser_cm = 0
            user.save()
        except:
            CLMException('cm_admin_add')

    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def change_password(cm_response, **data):
    """
    @clmview_admin_clm
    @cm_request_transparent{admin.change_password()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def list_admins(cm_response, **data):
    """
    @clmview_admin_clm
    @cm_request_transparent{admin.list_admins()}
    """
    return cm_response
