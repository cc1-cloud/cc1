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

"""@package src.clm.views.user.public_ip

@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from clm.utils.decorators import user_log, cm_request


@user_log(log=False, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    Returns list of caller's public IPs.

    @clmview_user
    @cm_request_transparent{user.public_ip.get_list()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def request(cm_response, **data):
    """
    Sends request to grant new public IP for caller. If caller's quota allowes,
    user will obtain new public IP.

    @clmview_user
    @cm_request_transparent{user.public_ip.request()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def assign(cm_response, **data):
    """
    Assigns public IP to caller's VM with id \c vm_id

    @clmview_user
    @cm_request_transparent{user.public_ip.assign()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def unassign(cm_response, **data):
    """
    Unassigns public IP from VM with given id. Unassigned public IP may be assigned
    to any of his VMs.

    @clmview_user
    @cm_request_transparent{user.public_ip.unassign()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def release(cm_response, **data):
    """
    Removes IP from callers public IP's pool and makes it available
    for other users to be further requested. Caller doesn't dispose this IP
    any more. He'll have to send another request if he needs more IPs.

    @clmview_user
    @cm_request_transparent{user.public_ip.release()}
    """
    return cm_response
