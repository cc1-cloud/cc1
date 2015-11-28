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

"""@package src.cm.views.guest.user
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
        Copy&paste: Maciej Nabozny
"""
from cm.utils.decorators import guest_log
from cm.models.user import User
from cm.utils import log
from cm.utils.exception import CMException


@guest_log(log=True)
def add(new_user_id):
    """
    Adds existing CLM User to CM Users.
    @cmview_guest
    @param_post{new_user_id,int} id of the existing CLM User

    @response{None}
    """
    user = User.create(new_user_id)
    try:
        user.save()
    except Exception, e:
        log.debug(0, "Adding to DB: %s" % str(e))
        raise CMException('user_create')
