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

"""@package src.clm.views.admin_cm.storage_image
@alldecoratedby{src.clm.utils.decorators.admin_cm_log}
"""
from clm.utils.decorators import admin_cm_log, cm_request
from clm.utils.cm import CM
from clm.utils.exception import CLMException
from clm.models.user import User


@admin_cm_log(log=False, pack=True)
def get_list(cm_id, caller_id, cm_password):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.get_list()}
    """
    names = {}
    resp = CM(cm_id).send_request("admin_cm/storage_image/get_list/", caller_id=caller_id, cm_password=cm_password)

    for img in resp['data']:
        if str(img['user_id']) not in names:
            try:
                user = User.objects.get(pk=img['user_id'])
                names[str(img['user_id'])] = user.first + " " + user.last
            except:
                raise CLMException('user_get')
        img['owner'] = names[str(img['user_id'])]

    return resp['data']


@admin_cm_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.get_by_id()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.delete(}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def edit(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.edit()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def download(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.download()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def set_public(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.set_public()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def set_private(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.set_private()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def copy(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage_image.copy()}
    """
    """
    return cm_response
