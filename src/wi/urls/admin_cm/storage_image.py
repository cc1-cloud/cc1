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

"""@package src.wi.urls.admin_cm.storage_image

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.storage_image import EditDiskForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import form_generic_id, simple_generic_id, direct_to_template


disk_patterns = patterns('wi.views.admin_cm.storage_image',
    url(r'^disks/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/disks.html'}, name='cma_disks'),
    url(r'^ajax/get_table_disks/$', 'cma_ajax_get_table_disks', name='cma_ajax_get_table_disks'),
    url(r'^ajax/edit_disk/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully edited selected disk.') % {'desc': desc}),
         'confirmation':        _('Save'),
         'request_url_both':    {'disk_controllers': 'user/storage_image/get_disk_controllers/'},
         'request_url_post':    'admin_cm/storage_image/edit/',
         'request_url_get':     'admin_cm/storage_image/get_by_id/',
         'id_key':              'storage_image_id',
         'form_class':          EditDiskForm,
         },
        name='cma_ajax_edit_disk'),
    url(r'^ajax/delete_disk/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted disk volume <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete disk volume <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/storage_image/delete/',
         'id_key':          'storage_image_id', },
        name='cma_ajax_delete_disk'),
    url(r'^ajax/cm/revoke_disk/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully revoked disk volume <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to revoke disk volume <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/storage_image/revoke/',
         'id_key':          'storage_image_id', },
        name='cma_ajax_revoke_disk'),

    url(r'^ajax/copy_disk/(?P<id1>\d+)/$', 'cma_ajax_copy_disk', name='cma_ajax_copy_disk'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(disk_patterns)),
)
