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

"""@package src.clm.views.admin_cm.node
@alldecoratedby{src.clm.utils.decorators.admin_cm_log}
"""

from clm.utils.decorators import admin_cm_log
from clm.utils.decorators import cm_request


@admin_cm_log(log=False, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.get_list()}
    """
    return cm_response


@admin_cm_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.get_by_id()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def lock(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.lock()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def unlock(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.unlock()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.delete()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def add(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.add()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def edit(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.edit()}
    """
    return cm_response


@admin_cm_log(log=False, pack=False)
@cm_request
def get_by_id_details(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.get_by_id_details()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def check(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{node.check()}
    """
    return cm_response
