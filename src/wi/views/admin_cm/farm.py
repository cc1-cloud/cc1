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

"""@package src.wi.views.admin_cm.farm
@author Piotr Wójcik
@date 26.03.2012
"""
from colorsys import hsv_to_rgb

from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from common.states import vm_states, farm_states
from wi.utils import messages_ajax
from wi.utils.decorators import admin_cm_permission
from wi.utils.decorators import django_view
from wi.utils.exceptions import RestErrorException
from wi.utils.formatters import time_from_sec
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import farm_states_reversed, vm_states_reversed
from wi.utils.views import prep_data


@django_view
@admin_cm_permission
def cma_farms(request, template_name='admin_cm/show_farms.html'):
    """
    CM admin farms list view.
    """
    all_users = []

    try:
        all_users = prep_data('admin_cm/user/get_list/', request.session)
    except RestErrorException as ex:
        messages.error(request, ex.value)

    return render_to_response(template_name, {'all_users': all_users}, context_instance=RequestContext(request))


@django_view
@ajax_request
@admin_cm_permission
def cma_farms_ajax_get_table(request, user_id):
    """
    Ajax view for fetching farms list.
    """
    if request.method == 'GET':
        farms = prep_data(('admin_cm/farm/get_list/', {'user_id': int(user_id)}), request.session)

        for farm in farms:
            farm['stateName'] = unicode(farm_states_reversed[farm['state']])

            for vm in farm['vms']:
                vm['pub_ip'] = []
                for i in vm['leases']:
                    if i['public_ip'] != "":
                        vm['pub_ip'].append(i['public_ip']['address'])

                vm['priv_ip'] = []
                for i in vm['leases']:
                    vm['priv_ip'].append(i['address'])

            farm['stringIP'] = ', '.join(farm['vms'][0]['priv_ip'])
            farm['stringPubIP'] = ', '.join(farm['vms'][0]['pub_ip'])
            farm['stringDisk'] = ', '.join([disk['name'] for disk in farm['vms'][0]['storage_images']])
            farm['stringISO'] = ', '.join([iso['name'] for iso in farm['vms'][0]['iso_images']])

        return messages_ajax.success(farms)


@django_view
@ajax_request
@admin_cm_permission
def cma_farms_ajax_details(request, id1, template_name='admin_cm/ajax/farm_details.html'):
    """
    Ajax view for fetching farm details.
    """
    if request.method == 'POST':
        owner = None

        farm = prep_data(('admin_cm/farm/get_by_id/', {'farm_id': id1}), request.session)

        owner = prep_data(('admin_cm/user/get_by_id/', {'user_id': farm['user_id']}), request.session)
        print owner
        farm['uptime'] = time_from_sec(farm['uptime'])
        farm['status'] = farm['state']

        for vm in farm['vms']:
            vm['stateName'] = unicode(vm_states_reversed[vm['state']])
            vm['pub_ip'] = []
            for i in vm['leases']:
                if i['public_ip'] != "":
                    vm['pub_ip'].append(i['public_ip']['address'])

            vm['priv_ip'] = []
            for i in vm['leases']:
                vm['priv_ip'].append(i['address'])

            vm['cpuLoadPercent'] = int(min(float(vm['cpu_load'].get('60') or 0) * 100, 100))
            vm['cpuLoadColor'] = "#%02x%02x%02x" % tuple(i * 255 for i in hsv_to_rgb(float(vm['cpuLoadPercent']) / 300, 1.0, 0.8))

        return messages_ajax.success(
                    render_to_string(template_name,
                                    {'farm_id': id1,
                                     'item': farm,
                                     'farm_states_reverse': farm_states_reversed,
                                     'farm_states': farm_states,
                                     'vm_states': vm_states,
                                     'owner': owner},
                                     context_instance=RequestContext(request)))
