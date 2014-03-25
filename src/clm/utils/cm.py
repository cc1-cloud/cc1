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

"""@package src.clm.utils.cm
"""

# from clm.utils import log
from clm.models.cluster import Cluster
from common.utils import ServerProxy


def CM(cm_id):
    """
    Returns ServerProxy for specified Cluster.

    @parameter{cm_id,int} id of the CM

    @returns{common.utils.ServerProxy} instance of CM proxy server
    """
    cluster = Cluster.get(cm_id)
    server = ServerProxy('http://%s:%s' % (cluster.address, cluster.port))
    return server
