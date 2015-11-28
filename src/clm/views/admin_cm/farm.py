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

"""@package src.clm.views.admin_cm.farm
"""

from clm.utils.decorators import admin_cm_log, cm_request
from clm.utils.cm import CM
from clm.models.user import User
from clm.utils.exception import CLMException


@admin_cm_log(log=False)
@cm_request
def get_list(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{farm.get_list()}
    """
    if cm_response['status'] != 'ok':
        raise CLMException('cm_error')

    names = {}
    for farm in cm_response["data"]:
        if str(farm['user_id']) not in names:
            try:
                user = User.objects.get(pk=farm['user_id'])
                names[str(farm['user_id'])] = "%s %s" % (user.first, user.last)
            except:
                raise CLMException('user_get')
        farm["owner"] = names[str(farm["user_id"])]

    return cm_response["data"]


@admin_cm_log(log=True, pack=False)
@cm_request
def destroy(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{farm.destroy()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{farm.get_by_id()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def erase(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{farm.erase()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def save_and_shutdown(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{farm.save_and_shutdown()}
    """
    return cm_response
