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

from clm.models.cluster import Cluster
from clm.utils.exception import CLMException
from common.utils import ServerProxy
from clm.utils import message


class CM:
    def __init__(self, cm_id):
        """
        Create object representing CM.

        @parameter{cm_id,int} id of the CM

        @returns{common.utils.ServerProxy} instance of CM proxy server
        """
        cluster = Cluster.get(cm_id)
        self.server = ServerProxy('http://%s:%s' % (cluster.address, cluster.port))

    def send_request(self, *args, **kw):
        """
        Make request to particular CM.
        """
        resp = self.server.send_request(*args, **kw)
        if resp['status'] != 'ok':
            raise CLMException(resp['status'])
        if 'messages' in resp:
            for user_id, msgs in resp['messages'].iteritems():
                for msg in msgs:
                    message.add(user_id, msg)
        return resp
