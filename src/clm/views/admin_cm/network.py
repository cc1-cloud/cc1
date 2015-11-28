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

"""@package src.clm.views.admin_cm.network
"""

from clm.utils.decorators import admin_cm_log, cm_request


@admin_cm_log(log=True, pack=False)
@cm_request
def add(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{network.add()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete_available_network(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{network.delete_available_network()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete_user_network(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{network.delete_user_network()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def list_available_networks(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{network.list_available_networks()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def list_user_networks(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request{iso_image.get_list()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def list_leases(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{network.list_leases()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def lock(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{network.lock()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def unlock(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{network.unlock()}
    """
    return cm_response
