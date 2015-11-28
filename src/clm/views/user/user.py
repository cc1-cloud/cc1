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

"""@package src.clm.views.user.user
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from django.conf import settings

from clm.models.cluster import Cluster
from clm.models.user import User
from clm.utils import mail
from clm.utils.decorators import user_log, cm_request
from clm.utils.exception import CLMException
from common.states import cluster_states


@user_log(log=True)
def get_my_data(cm_id, caller_id):
    """
    Returns user's data.

    @clmview_user
    """
    user = User.get(caller_id)
    user = user.dict
    endpoints = []
    for cm_name in [c.short_dict['name'] for c in Cluster.objects.filter(state=cluster_states['ok'])]:
        endpoints.append(cm_name + "." + settings.EC2_URL)
    user["ec2_endpoints"] = endpoints
    return user


@user_log(log=True)
def set_password(cm_id, caller_id, new_password):
    """
    Sets user's password.

    @clmview_user
    @param_post{new_password,string}
    """
    user = User.get(caller_id)
    user.password = new_password
    try:
        user.save()
    except:
        raise CLMException('user_set_password')

    return user.dict


@user_log(log=True)
def edit(cm_id, caller_id, email, default_cluster_id):
    """
    Function for editing user's data.

    @clmview_user
    @param_post{email,string}
    @param_post{default_cluster_id}

    @response{dict} new user's info
    """

    user = User.get(caller_id)
    user.email = email
    user.default_cluster_id = default_cluster_id
    try:
        user.save()
    except:
        raise CLMException('user_edit')

    return user.dict


@user_log(log=True, pack=False)
@cm_request
def check_quota(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.user.get_quota()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def points_history(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.user.point_history()}
    """
    return cm_response


@user_log(log=True)
def send_issue(cm_id, caller_id, topic, issue):
    """
    Send issue email

    @clmview_user
    @param_post{topic,string} topic of the issue email
    @param_post{issue,string} content of the issue email
    """
    try:
        mail.send(settings.ISSUE_EMAIL, issue, topic)
    except Exception:
        raise CLMException('send_issue_error')
