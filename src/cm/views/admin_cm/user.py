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

"""@package src.cm.views.admin_cm.user
@alldecoratedby{src.cm.utils.decorators.admin_cm_log} (except for \c add)

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""
from cm.utils.exception import CMException
from cm.models.user import User
from cm.utils.decorators import admin_cm_log, user_log


@user_log(log=True)
def add(caller_id, user_id):
    """
    Function adds new user to DB and creates its home directory.
    @cmview_user

    @note This method is decorated by user_log decorator, not by admin_cm_log.
    This is caused by the fact that CLMAdmin doesn't need to be CMAdmin and
    despite not having rights to call CMAdmin functions he needs to call it on
    CMAdmin priviledges.

    @parameter{user_id}

    @response{None}
    """

    User.create(user_id)


@admin_cm_log(log=True)
def change_quota(caller_id, user_id, memory, cpu, storage, public_ip, points):
    """
    Function changes quota for user @prm{user_id}.
    @cmview_admin_cm

    @parameter{user_id}
    @parameter{memory}
    @parameter{cpu,int}
    @parameter{storage,int}
    @parameter{public_ip,int}
    @parameter{points,int}
    """

    user = User.get(user_id)

    user.memory = memory
    user.cpu = cpu
    user.storage = storage
    user.public_ip = public_ip
    user.points = points

    try:
        user.save()
    except:
        raise CMException('user_change_quota')


# changes quota of multiple users
@admin_cm_log(log=True)
def multiple_change_quota(caller_id, user_ids, memory=None, cpu=None, storage=None, public_ip=None, points=None):
    """
    Method changes quota of multiple users.
    @cmview_admin_cm

    @dictkey{users,list(int)} ids of the users to change quota
    @dictkey{cpu,int} cpu to set
    @dictkey{storage,int} storage to set
    @dictkey{public_ip,int} number of public_ips to set
    @dictkey{points,int} points to set

    @response{None}
    """

    for user_id in user_ids:
        user = User.get(user_id)
        user.memory = memory or user.memory
        user.cpu = cpu or user.cpu
        user.storage = storage or user.storage
        user.public_ip = public_ip or user.public_ip
        user.points = points or user.points
        try:
            user.save()
        except:
            raise CMException('user_change_quota')


@admin_cm_log(log=True)
def check_quota(caller_id, user_id):
    """
    Check quota of the user @prm{user_id}.
    @cmview_admin_cm

    @parameter{user_id,int}

    @response{dict} extended user's data
    """
    return User.get(user_id).long_dict


@admin_cm_log(log=False)
def get_list(caller_id):
    """
    Returns all users.
    @cmview_admin_cm

    @parameter{caller_id,int}

    @response{list(dict)} dicts describing all users
    """

    return [user.long_dict for user in User.objects.all()]
