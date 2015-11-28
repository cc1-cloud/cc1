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

"""@package src.clm.views.admin_cm.user
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from clm.models.user import User
from clm.utils.cm import CM
from clm.utils.decorators import admin_cm_log, cm_request
from clm.utils.exception import CLMException


@admin_cm_log(log=True, pack=False)
@cm_request
def add(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{user.add()}
    """
    return cm_response


@admin_cm_log(log=False, pack=True)
def get_by_id(cm_id, caller_id, cm_password, user_id):
    """
    @clmview_admin_cm
    @param_post{user_id,int}
    @response{dict} dict property of the requested User
    """
    user = User.get(user_id)
    return user.dict


@admin_cm_log(log=True, pack=True)
def get_list(cm_id, caller_id, cm_password):
    """
    Method returns list of Users of the managed cluster

    @cm_request{storage_image.get_list()}
    @clmview_admin_cm
    @param_post{short,bool} caller's CM admin password

    @response{list(dict)} dicts property for each requested cluster's User
    """
    r = CM(cm_id).send_request("admin_cm/user/get_list/", cm_password=cm_password, caller_id=caller_id)
    if r['status'] != 'ok':
        raise CLMException(r['status'])
    # build dictionary 'id':'dict from cm'
    d = {}
    ret = {}
    for i in r['data']:
        d[i['user_id']] = i
    for user in User.objects.filter(id__in=d.keys()):
        ret[user.id] = d[user.id]
        ret[user.id].update(user.dict)

    return ret.values()


@admin_cm_log(log=True, pack=False)
@cm_request
def check_quota(cm_response, **data):
    """
    Method returns state of user's quota.

    @clmview_admin_cm
    @cm_request_transparent{user.get_quota()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def change_quota(cm_response, **data):
    """
    Changes quota (CPU, storage, public IPs count and points)
    as described by \c data.

    @clmview_admin_cm
    @cm_request{user.change_quota()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def multiple_change_quota(cm_response, **data):
    """
    Method changes quota as described by \c data.

    @clmview_admin_cm
    @cm_request_transparent{user.multiple_change_quota()}
    """
    return cm_response
