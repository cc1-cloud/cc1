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

"""@package src.clm.views.guest.cluster
@alldecoratedby{src.clm.utils.decorators.guest_log}
"""

from clm.models.cluster import Cluster
from clm.utils.decorators import guest_log
from common.states import cluster_states


@guest_log(log=False)
def list_names():
    """
    @clmview_guest
    @response{list(dict)} list of clusters data, Cluster.short_dict() property
    for each unlocked Cluster
    """
    return [c.short_dict for c in Cluster.objects.filter(state=cluster_states['ok'])]
