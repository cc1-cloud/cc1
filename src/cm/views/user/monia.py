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

"""@package src.cm.views.user.monia
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Wojtoń
"""

from cm.utils.decorators import user_log
from cm.utils.monia import RrdHandler
from common.states import stat_resolutions, stat_names, stat_ranges


@user_log(log=False)
def vm_stats(caller_id, vm_id, stat_name, time, stat_range, resolution):
    """
    Returns statistics for specified VM.

    @cmview_user
    @param_post{vm_id,int}
    @param_post{stat_name,string} type of required statistics
    @param_post{time,string} time of last row
    @param_post{stat_range,string} period of time from @prm{time} to past
    @param_post{resolution,string} statistics resolution

    @response{dict} list of the total usage of VM resources from start VM
    """

    if type(stat_name) is int:
        stat_name = [stat_name]

    n = []
    for stat in stat_name:
        n.append(stat_names.keys()[stat_names.values().index(stat)])
    p = int(stat_ranges.keys()[stat_ranges.values().index(int(stat_range))])
    r = int(stat_resolutions.keys()[stat_resolutions.values().index(resolution)])

    return RrdHandler().get_vm_stats('vm-%d-%d' % (vm_id, caller_id), n, int(time) - p, time, r)
