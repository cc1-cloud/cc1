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

"""@package src.clm.views.admin_cm.admin
@alldecoratedby{src.clm.utils.decorators.admin_cm_log}
"""
from clm.utils.decorators import admin_cm_log, cm_request, user_log


@admin_cm_log(log=True, pack=False)
@cm_request
def check_password(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request_transparent{admin.check_password()}
    """
    return cm_response


@user_log(log=True, pack=False)
def am_i_admin(cm_response, **data):
    """
    @clmview_admin_cm
    @cm_request{admin.am_i_admin()}
    """
    return cm_response
