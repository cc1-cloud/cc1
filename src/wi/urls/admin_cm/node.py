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

"""@package src.wi.urls.admin_cm.node

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from common.states import image_access
from django.conf.urls import url, patterns, include
from django.utils.translation import ungettext, ugettext_lazy as _
from wi.forms.node import NodeForm, EditNodeForm
from wi.forms.vm import CreateVMOnNodeForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import generic_multiple_id, form_generic_id, \
    direct_to_template, simple_generic_id, form_generic


node_patterns = patterns('wi.views.admin_cm.node',
    url(r'^nodes/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/nodes.html'}, name='cma_nodes'),
    url(r'^ajax/get_table_nodes/$', 'cma_ajax_get_table_nodes', name='cma_ajax_get_table_nodes'),
    url(r'^ajax/node_details/(?P<node_id>\d+)/$', 'cma_ajax_node_details', name='cma_ajax_node_details'),
    url(r'^ajax/delete_node/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted node <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete node <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/node/delete/',
         'id_key':          'node_id', },
        name='cma_ajax_delete_node'),

    url(r'^ajax/cm/lock_node/$', admin_cm_permission(generic_multiple_id),
        {'template_name':       'generic/simple.html',
         'success_msg':         (lambda desc, count: ungettext('You have successfully locked node <b>%(desc)s</b>.', 'You have successfully locked %(count)d nodes (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Do you want to lock node <b>%(desc)s</b>?', 'Do you want to lock %(count)d nodes <b>%(desc)s</b>?', count) % {'desc': desc, 'count': count}),
         'request_url':         'admin_cm/node/lock/',
         'id_key':              'node_id_list'
         },
        name='cma_ajax_lock_node'),
    url(r'^ajax/hardlock_node/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully hardlocked node <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to hardlock node <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/node/hardlock/',
         'id_key':          'node_id', },
        name='cma_ajax_hardlock_node'),
    url(r'^ajax/unlock_node/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully unlocked node <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to unlock node <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/node/unlock/',
         'id_key':          'node_id', },
        name='cma_ajax_unlock_node'),
    url(r'^ajax/add_node/$', admin_cm_permission(form_generic),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully created a node.') % {'desc': desc}),
         'confirmation':        _('Create'),
         'request_url_post':   'admin_cm/node/add/',
         'form_class':          NodeForm},
        name='cma_ajax_add_node'),
    url(r'^ajax/edit_node/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully edited selected node.') % {'desc': desc}),
         'confirmation':        _('Save'),
         'request_url_post':    'admin_cm/node/edit/',
         'request_url_get':     'admin_cm/node/get_by_id/',
         'id_key':              'node_id',
         'form_class':          NodeForm},
        name='cma_ajax_edit_node'),
    url(r'^ajax/create_vm/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully created a virtual machine on selected node (address: %(desc)s).') % {'desc': desc}),
         'confirmation':        _('Create'),
         'request_url_post':    'admin_cm/vm/create/',
         'id_key':              'node_id',
         'form_class':           CreateVMOnNodeForm,
         'request_url_both':    {'images_public': ('user/system_image/get_list/', {'access': image_access['public']}),
                                   'images_private': ('user/system_image/get_list/', {'access': image_access['private']}),
                                   'images_group': ('user/system_image/get_list/', {'access': image_access['group']}),
                                   'templates': 'user/template/get_list/',
                                   'ips': 'user/public_ip/get_list/',
                                   'disks': 'user/storage_image/get_list/',
                                   'iso': 'user/iso_image/get_list/',
                                   }
         },
        name='cma_ajax_create_vm'),
    url(r'^ajax/mount_storage/(?P<node_id>\d+)/$', 'cma_ajax_mount_storage', name='cma_ajax_mount_storage'),

)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(node_patterns)),
)
