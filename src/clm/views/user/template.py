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

"""@package src.clm.views.user.template
@author Gaetano
@date May 9, 2013
"""

from clm.utils.decorators import user_log, cm_request


@user_log(log=False, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.template.get_list()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{user.template.get_by_id()}
    """
    return cm_request
