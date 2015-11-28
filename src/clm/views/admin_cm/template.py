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

"""@package src.clm.views.admin_cm.template
"""

from clm.utils.decorators import admin_cm_log, cm_request


@admin_cm_log(log=True)
@cm_request
def add(cm_response, **data):
    """
    Creates template of VM. Template has a name and some description.
    It defines VM's hardware parameters: CPU and memory. It also defines
    number of points utilized by VM created of it (per hour and overly).

    @clmview_admin_cm
    @cm_request_transparent{user.add()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    Deletes template from available templates.

    @clmview_admin_cm
    @cm_request_transparent{user.delete()}
    """
    return cm_response


@admin_cm_log(log=True)
@cm_request
def edit(cm_response, **data):
    """
    Edits Template's components.

    @clmview_admin_cm
    @cm_request_transparent{user.edit()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    Returns list of available Templates.

    @clmview_admin_cm
    @cm_request_transparent{user.get_list()}
    """
    return cm_response


@admin_cm_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    Returns requested Template.

    @clmview_admin_cm
    @cm_request_transparent{user.get_by_id()}
    """
    return cm_response
