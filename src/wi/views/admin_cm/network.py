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

"""@package src.wi.views.admin_cm.network
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 19.10.2012
"""
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from wi.utils import messages_ajax
from wi.utils.decorators import admin_cm_permission
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import pool_states_reversed
from wi.utils.views import prep_data


@django_view
@admin_cm_permission
def cma_networks(request, template_name='admin_cm/networks.html'):
    """
    View rendering network list.
    """
    rest_data = prep_data('admin_cm/user/get_list/', request.session)
    return render_to_response(template_name, {'all_users': rest_data}, context_instance=RequestContext(request))


@django_view
@ajax_request
@admin_cm_permission
def cma_networks_ajax_get_table(request, user_id):
    """
    Ajax view returning network list.
    """
    if request.method == 'GET':
        networks = prep_data(('admin_cm/network/list_user_networks/', {'user_id': int(user_id)}), request.session)
        return messages_ajax.success(networks)


@django_view
@ajax_request
@admin_cm_permission
def cma_networks_ajax_network_details(request, network_id, template_name='admin_cm/ajax/network_details.html'):
    """
    Ajax view fetching network details.
    """
    if request.method == 'POST':
        net = prep_data(('admin_cm/network/list_leases/', {'network_id': network_id}), request.session)

        return messages_ajax.success(render_to_string(template_name, {'id': int(network_id),
                                                                      'item': net},
                                                      context_instance=RequestContext(request)))


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_pool_table(request):
    """
    Ajax view fetching pool list.
    """
    if request.method == 'GET':
        pools = prep_data('admin_cm/network/list_available_networks/', request.session)

        for pool in pools:
            pool['stateName'] = unicode(pool_states_reversed[pool['state']])

        return messages_ajax.success(pools)
