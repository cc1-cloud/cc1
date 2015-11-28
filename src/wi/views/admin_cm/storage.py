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

"""@package src.wi.views.admin_cm.storage
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.02.2012
"""
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.forms.node import MountNodeForm
from wi.utils import messages_ajax
from wi.utils.decorators import admin_cm_permission
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import storage_states_reversed as storage_states
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_table_storages(request):
    """
    Ajax view returning storages list.
    """
    if request.method == 'GET':
        storages = prep_data('admin_cm/storage/get_list/', request.session)

        for item in storages:
            item['stateName'] = unicode(storage_states[item['state']])
            item['capacity'] = filesizeformatmb(item['capacity'])

        return messages_ajax.success(storages)


@django_view
@ajax_request
@admin_cm_permission
@csrf_protect
def cma_ajax_mount_node(request, storage_id, template_name='generic/form.html', form_class=MountNodeForm):
    """
    Ajax view for storage to node mounting.
    """
    rest_data = prep_data({'nodes': 'admin_cm/node/get_list/'}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            rest_data2 = prep_data({'storages': ('admin_cm/storage/mount/', [{'storage_id': int(storage_id),
                                                                                        'node_id': int(form.cleaned_data['node_id'])}]),
                                        }, request.session)

            storages = rest_data2['storages']

            all_ok = True
            for key in storages.keys():
                for key2 in storages[key].keys():
                    if storages[key][key2] != 'mounted':
                        all_ok = False
            if all_ok:
                return messages_ajax.success(_('You have successfully mounted storage(s) to selected node.'))
            else:
                resp = []
                for key in storages.keys():
                    for key2 in storages[key].keys():
                        if storages[key][key2] != 'mounted':
                            resp.append({'type': 'storage-node',
                                         'storage_id': key,
                                         'node_id': key2,
                                         'status_text': storages[key][key2]
                                        })
                return messages_ajax.success(resp, 7999)
    else:
        form = form_class(rest_data=rest_data)
    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'confirmation': _('Mount'),
                                                                  'text': ''},
                                                   context_instance=RequestContext(request)),
                                status=1)
