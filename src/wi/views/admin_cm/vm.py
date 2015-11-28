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

"""@package src.wi.views.admin_cm.vm
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.02.2012
"""
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from common.states import vm_states
from wi.models.user import parse_user
from wi.utils import messages_ajax
from wi.utils.decorators import admin_cm_permission
from wi.utils.decorators import django_view
from wi.utils.formatters import time_from_sec
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import vm_states_reversed
from wi.utils.views import prep_data


@django_view
@admin_cm_permission
def cma_vms(request, template_name='admin_cm/show_vm.html'):
    """
    View handling the page embeding the VM list.
    """
    users = prep_data('admin_cm/user/get_list/', request.session)
    return render_to_response(template_name, {'all_users': users}, context_instance=RequestContext(request))


@django_view
@ajax_request
@admin_cm_permission
def cma_vms_ajax_get_table(request, user_id):
    """
    Ajax view for fetching VM list.
    """
    if request.method == 'GET':

        vms = prep_data(('admin_cm/vm/get_list/', {'user_id': int(user_id)}), request.session)

        for item in vms:
            item['stateName'] = unicode(vm_states_reversed[item['state']])
            item['pub_ip'] = []
            for i in item['leases']:
                if i['public_ip'] != "":
                    item['pub_ip'].append(i['public_ip']['address'])
            item['stringIP'] = ', '.join(item['pub_ip'])
            item['stringISO'] = ', '.join([iso['name'] for iso in item['iso_images']])
            item['stringDisk'] = ', '.join([disk['name'] for disk in item['storage_images']])

        return messages_ajax.success(vms)


@django_view
@ajax_request
@admin_cm_permission
def cma_vms_ajax_vm_details(request, vm_id, template_name='admin_cm/ajax/vm_details.html'):
    """
    Ajax view for fetching VM details.
    """
    if request.method == 'POST':

        vm = prep_data(('admin_cm/vm/get_by_id/', {'vm_id': vm_id}), request.session)

        rest_data2 = prep_data({'user': ('admin_cm/user/get_by_id/', {'user_id': vm['user_id']})}, request.session)
        owner = parse_user(rest_data2['user'])

        if vm['state'] == vm_states['closed']:
            return messages_ajax.success('', status=1)

        vm['uptime'] = time_from_sec(vm['uptime'])

        return messages_ajax.success(
                    render_to_string(template_name,
                                    {'vm_id': vm_id,
                                     'item': vm,
                                     'states_reversed': vm_states_reversed,
                                     'states': vm_states,
                                     'owner': owner},
                                     context_instance=RequestContext(request)))
