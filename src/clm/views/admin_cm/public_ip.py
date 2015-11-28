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

from clm.utils.decorators import admin_cm_log, cm_request


@admin_cm_log(log=False, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{public_ip.get_list()}
    """
    names = {}

    for ip in cm_response['data']:
        if ip['user_id'] == '':
            ip['owner'] = ''
        elif str(ip['user_id']) not in names:
            try:
                user = User.objects.get(pk=ip['user_id'])
                names[str(ip['user_id'])] = user.first + " " + user.last
            except:
                raise CLMException('user_get')
            ip['owner'] = names[str(ip['user_id'])]

    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def add(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{public_ip.add()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{public_ip.delete()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def unassign(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{public_ip.unassign()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def release(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{public_ip.release()}
    """
    return cm_response
    """
    @clmview_admin_cm
    @cm_request_transparent{public_ip.revoke()}
    """
