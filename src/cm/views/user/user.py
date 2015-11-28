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

"""@package src.cm.views.user.user
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""

from cm.utils.exception import CMException
from cm.models.user import User
from cm.utils.decorators import user_log
from clm.utils import log


# Check quota for caller user.
@user_log(log=True)
def check_quota(caller_id):
    """
    Check quota for caller user.

    @cmview_user

    @response{dict} extended caller's data
    """
    return User.get(caller_id).long_dict


@user_log(log=True)
def points_history(caller_id):
    """
    @cmview_user

    @response caller's point history
    """
    return User.get(caller_id).points_history()


@user_log(log=True)
def add_missing(caller_id, remote):
    """
    Adds Users whose ids are listed in @prm{remote} and who are locally
    missing.

    @cmview_user
    @param_post{remote,list(int)} ids of the remote Users
    """

    # remote must be passed through POST as a list
    # it is a list of users id
    try:
        # put all the user ids in a list
        local = User.objects.all().values_list('id', flat=True)
        # create user for all the ids which are in remote but not in the local cm
        for user_id in [uid for uid in remote if uid not in local]:
            User.create(user_id)
    except:
        raise CMException('user_create')
