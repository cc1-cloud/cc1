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

"""@package src.clm.views.admin_cm.cluster
"""
from clm.models.cluster import Cluster
from clm.utils.decorators import admin_cm_log


@admin_cm_log(log=False)
def get_data(cm_id, caller_id, cm_password):
    """
    Returns dictionary describing current cluster.
    @clmview_admin_cm
    @clm_view_transparent{cluster.get_data()}
    """
    return Cluster.objects.get(pk=cm_id).dict
