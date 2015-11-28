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
from clm.utils.cm import CM
from clm.models.user import User
from common.states import group_states
from clm.utils.exception import CLMException


@user_log(log=True, pack=False)
def create(cm_id, caller_id, **data):
    """
    @clmview_user
    """
    user = User.get(caller_id)
    groups = list(user.group_set.filter(usergroup__status__exact=group_states['ok']).values_list('id', flat=True))
    return CM(cm_id).send_request("user/farm/create/", caller_id=caller_id, groups=groups, **data)


@user_log(log=True, pack=False)
@cm_request
def destroy(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.farm.destroy()}
    """
    return cm_response


@user_log(log=True)
@cm_request
def get_list(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.farm.get_list()}
    """
    d = {}
    r = cm_response['data']
    for farm in r:
        if farm['user_id'] not in d:
            try:
                u = User.objects.get(pk=farm['user_id'])
                d[farm['user_id']] = u.first + " " + u.last
            except User.DoesNotExist:
                raise CLMException('user_get')
        farm['owner'] = d[farm['user_id']]
    return r


@user_log(log=True, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.farm.get_by_id()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def save_and_shutdown(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.farm.save_and_shutdown()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def check_resources(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.farm.check_resources()}
    """
    return cm_response
