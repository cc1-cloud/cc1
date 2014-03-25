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

"""@package src.wi.views.admin_cm.cm
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 17.10.2011
"""

from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.utils import messages_ajax
from wi.utils.decorators import admin_cm_permission, django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import cm_active_reversed as cm_states, \
    node_states_reversed as node_states
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_cm_data(request):
    """
    Ajax view for fetching CM data (quotas etc.).
    """
    if request.method == 'GET':
        rest_data = prep_data({'cm_data': 'admin_cm/cluster/get_data/',
                               'nodes': 'admin_cm/node/get_list/'
                              }, request.session)

        data = rest_data['cm_data']

        total_cpu = 0
        total_mem = 0
        free_cpu = 0
        free_mem = 0
        for node in rest_data['nodes']:
            node['stateName'] = unicode(node_states[node['state']])
            if node['state'] == 1:
                free_cpu += node['cpu_free']
                free_mem += node['memory_free']
                total_cpu += node['cpu_total']
                total_mem += node['memory_total']

        data['free_cpu'] = free_cpu
        data['free_mem'] = filesizeformatmb(free_mem)
        data['total_cpu'] = total_cpu
        data['total_mem'] = filesizeformatmb(total_mem)

        data['stateName'] = unicode(cm_states[data['state']])

        return messages_ajax.success(data)
