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

"""@package src.cm.views.ci.node
@author Maciej Nabozny <mn@mnabozny.pl>
@alldecoratedby{src.cm.utils.decorators.ci_log}
"""

from cm.utils.decorators import ci_log
from cm.models.node import Node
from cm.utils.exception import CMException
from common.states import node_states
import datetime


@ci_log(log=True)
def update_state(remote_ip, state, comment="", error=""):
    """
    @cmview_ci
    @param_post{remote_ip,string}
    @param_post{state}
    @param_post{comment,string}
    @param_post{error,string}
    """
    try:
        node = Node.objects.get(address=remote_ip)
    except:
        raise CMException('node_not_found')

    if node.state == node_states['locked']:
        return

    node.state = state
    if comment != "":
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        node.errors = "%s: %s" % (date, comment)
    else:
        node.errors = ""
    node.save()
