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

"""@package src.wi.urls.admin_cm.network

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _, ungettext

from wi.forms.network import AddPoolForm
from wi.forms.public_ip import AddPublicIPForm
from wi.forms.vm import MonitoringVMForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import form_generic_id, direct_to_template, \
    simple_generic_id, form_generic, get_list_generic, generic_multiple_id


network_patterns = patterns('wi.views.admin_cm.network',
    url(r'^networks/$', 'cma_networks', name='cma_networks'),
    url(r'^ajax/cm/networks_get_table/(?P<user_id>\d+)/$', 'cma_networks_ajax_get_table', name='cma_networks_ajax_get_table'),
    url(r'^ajax/cm/network_details/(?P<network_id>\d+)/$', 'cma_networks_ajax_network_details', name='cma_networks_ajax_network_details'),
    url(r'^ajax/remove_network/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully released network <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to release network <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/network/delete_user_network/',
         'id_key':          'network_id', },
        name='cma_ajax_remove_network'),

    url(r'^pools/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/pools.html'}, name='cma_pools'),
    url(r'^ajax/pools_table/$', 'cma_ajax_get_pool_table',
        name='cma_ajax_get_pool_table'),
    url(r'^ajax/add_pool/$', admin_cm_permission(form_generic),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully added a pool.') % {'desc': desc}),
         'confirmation':        _('Add'),
         'request_url_post':    'admin_cm/network/add/',
         'form_class':          AddPoolForm},
        name='cma_ajax_add_pool'
        ),
    url(r'^ajax/delete_pool/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted pool <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete pool <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/network/delete_available_network/',
         'id_key':          'pool_id',
         },
        name='cma_ajax_delete_pool'),
    url(r'^ajax/lock_pool/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully locked pool <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to lock pool <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/network/lock/',
         'id_key':          'pool_id', },
        name='cma_ajax_lock_pool'),
    url(r'^ajax/unlock_pool/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully unlocked pool <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to unlock pool <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/network/unlock/',
         'id_key':          'pool_id', },
        name='cma_ajax_unlock_pool'),

    url(r'^publicips/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/publicips.html'}, name='cma_publicips'),
    url(r'^ajax/publicips_table/$', admin_cm_permission(get_list_generic), {'request_url': 'admin_cm/public_ip/get_list/'},
        name='cma_ajax_get_publicips_table'),
    url(r'^ajax/add_publicip/$', admin_cm_permission(form_generic),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully added public IPs.') % {'desc': desc}),
         'confirmation':        _('Add'),
         'request_url_post':    'admin_cm/public_ip/add/',
         'form_class':          AddPublicIPForm},
        name='cma_ajax_add_publicip'),
    url(r'^ajax/cm/publicip_delete/$', admin_cm_permission(generic_multiple_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc, count: ungettext('You have successfully deleted Public IP <b>%(desc)s</b>.', 'You have successfully deleted %(count)d pulic IPs (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':         (lambda desc, count: ungettext('Do you want to delete public IP <b>%(desc)s</b>?', 'Do you want to delete %(count)d public IPs <b>%(desc)s</b>?', count) % {'desc': desc, 'count': count}),
         'request_url':     'admin_cm/public_ip/delete/',
         'id_key':          'public_ip_id_list', },
        name='cma_ajax_delete_publicips'),
    url(r'^ajax/cm/publicip_release/$', admin_cm_permission(generic_multiple_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc, count: ungettext('You have successfully released Public IP <b>%(desc)s</b>.', 'You have successfully released %(count)d pulic IPs (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':         (lambda desc, count: ungettext('Do you want to release public IP <b>%(desc)s</b>?', 'Do you want to release %(count)d public IPs <b>%(desc)s</b>?', count) % {'desc': desc, 'count': count}),
         'request_url':     'admin_cm/public_ip/release/',
         'id_key':          'public_ip_id_list', },
        name='cma_ajax_release_publicips'),

    url(r'^ajax/monitoring/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':        'vms/ajax/monitoring.html',
         'form_class':           MonitoringVMForm,
         'success_msg':         (lambda desc, data: data),
         'request_url_post':    'admin_cm/monia/vm_stats/',
         'id_key':              'vm_id', },
        name='cma_ajax_vm_monitoring'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(network_patterns)),
)
