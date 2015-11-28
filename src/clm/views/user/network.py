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

"""@package src.clm.views.user.network
@alldecoratedby{src.clm.utils.decorators.user_log}
@alldecoratedby{src.clm.utils.decorators.cm_request}
"""

from clm.utils.decorators import user_log, cm_request


@user_log(log=True, pack=False)
@cm_request
def request(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.network.requests()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def release(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.network.release()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def list_available_networks(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.network.list_available_networks()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def list_user_networks(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.network.list_user_networks()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def list_leases(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.network.list_leases()}
    """
    return cm_response
