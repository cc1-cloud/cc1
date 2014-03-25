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

"""@package src.wi.urls.admin_cm.storage
@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.storage import StorageForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import direct_to_template, simple_generic_id, form_generic

storage_patterns = patterns('wi.views.admin_cm.storage',
    url(r'^storages/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/storages.html'}, name='cma_storages'),
    url(r'^ajax/get_table_storages/$', 'cma_ajax_get_table_storages', name='cma_ajax_get_table_storages'),
    url(r'^ajax/add_storage/$', admin_cm_permission(form_generic),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully created a storage.') % {'desc': desc}),
         'confirmation':        _('Create'),
         'request_url_post':    'admin_cm/storage/create/',
         'form_class':          StorageForm},
        name='cma_ajax_add_storage'),
    url(r'^ajax/lock_storage/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully locked storage <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to lock storage <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/storage/lock/',
         'id_key':          'storage_id', },
        name='cma_ajax_lock_storage'),
    url(r'^ajax/delete_storage/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted storage <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete storage <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/storage/delete/',
         'id_key':          'storage_id', },
        name='cma_ajax_delete_storage'),
    url(r'^ajax/unlock_storage/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully unlocked storage <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to unlock storage <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/storage/unlock/',
         'id_key':          'storage_id', },
        name='cma_ajax_unlock_storage'),
    url(r'^ajax/mount_node/(?P<storage_id>\d+)/$', 'cma_ajax_mount_node', name='cma_ajax_mount_node'),

    url(r'^ajax/mount_rm/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully mounted strorage to RM.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to mount storage to RM?') % {'desc': desc}),
         'request_url':     'admin_cm/storage/mount_rm/',
         'id_key':          'storage_id', },
        name='cma_ajax_mount_rm'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(storage_patterns)),
)
