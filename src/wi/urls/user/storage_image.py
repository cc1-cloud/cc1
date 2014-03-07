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

"""@package src.wi.urls.user.storage_image
@author Piotr Wójcik
@date 19.11.2010
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from wi.forms.storage_image import ConvertImageForm, EditDiskForm
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, simple_generic_id, \
    form_generic_id

resources_patterns = patterns('wi.views.user.storage_image',

    url(r'^disks/$', user_permission(direct_to_template), {'template_name': 'resources/disks.html'}, name='res_disks'),
    url(r'^ajax/disk_table/$', 'res_ajax_get_disk_table', name='res_ajax_get_disk_table'),
    url(r'^ajax/upload_disk_http/$', 'res_ajax_upload_disk_http', name='res_ajax_upload_disk_http'),
    url(r'^ajax/add_disk/$', 'res_ajax_add_disk', name='res_ajax_add_disk'),
    url(r'^ajax/edit_disk/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully edited selected disk.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('Edit disk data:') % {'desc': desc}),
         'confirmation':         _('Save'),
         'request_url_post':     'user/storage_image/edit/',
         'request_url_get':      'user/storage_image/get_by_id/',
         'request_url_both':     {'disk_controllers': 'user/storage_image/get_disk_controllers/'},
         'id_key':               'storage_image_id',
         'form_class':           EditDiskForm},
        name='res_ajax_edit_disk'),
    url(r'^ajax/delete_disk/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully removed disk volume <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you really want to delete disk volume <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/storage_image/delete/',
         'id_key':          'storage_image_id',
         },
        name='res_ajax_delete_disk'),

    url(r'^ajax/change_to_image/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':   'generic/form.html',
         'success_msg':     (lambda desc, data: _('You have successfully changed disk <b>%(desc)s</b> to a VM image.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to change disk <b>%(desc)s</b> to a VM image?') % {'desc': desc}),
         'request_url_post':     'user/storage_image/convert_to_system_image/',
         'request_url_both':     {'disk_controllers': 'user/system_image/get_disk_controllers/',
                                  'video_devices':  'user/system_image/get_video_devices/',
                                  'network_devices': 'user/system_image/get_network_devices/', },
         'confirmation':    _('Change'),
         'id_key':          'storage_image_id',
         'form_class':      ConvertImageForm, },
        name='img_ajax_change_to_image'),
    )

urlpatterns = patterns('',
    url(r'^resources/', include(resources_patterns)),
)
