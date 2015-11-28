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

"""@package src.clm.views.admin_cm.storage
@alldecoratedby{src.clm.utils.decorators.admin_cm_log}
"""

from clm.utils.decorators import admin_cm_log, cm_request


@admin_cm_log(log=True, pack=False)
@cm_request
def create(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage.create()}
    """
    return cm_response


@admin_cm_log(log=False, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage.get_list()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def lock(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage.lock()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def unlock(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage.unlock()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def mount(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage.mount()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def check(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{storage.check()}
    """
    return cm_response
