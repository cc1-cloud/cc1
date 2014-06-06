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

"""@package src.wi.urls.user.system_image
@author Piotr Wójcik
@date 19.11.2010
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from wi.forms.system_image import EditImageForm, AssignGroupForm
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, simple_generic_id, \
    form_generic_id

images_patterns = patterns('wi.views.user.system_image',
    url(r'^$', user_permission(direct_to_template), {'template_name': 'images/base.html'}, name='img_images'),
    url(r'^images_private/$', user_permission(direct_to_template), {'template_name': 'images/images_private.html'},
        name='img_images_private'),
    url(r'^images_group/$', user_permission(direct_to_template), {'template_name': 'images/images_group.html'},
        name='img_images_group'),
    url(r'^images_public/$', user_permission(direct_to_template), {'template_name': 'images/images_public.html'},
        name='img_images_public'),

    url(r'^ajax/delete/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully removed image <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you really want to delete image <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/system_image/delete/',
         'id_key':          'system_image_id',
         },
        name='img_ajax_delete'),
    url(r'^ajax/get_all_table/(?P<img_type>\w+)/$', 'img_ajax_get_all_table', name='img_ajax_get_all_table'),
    url(r'^ajax/get_private_table/$', 'img_ajax_get_private_table', name='img_ajax_get_private_table'),
    url(r'^ajax/get_group_table/$', 'img_ajax_get_group_table', name='img_ajax_get_group_table'),
    url(r'^ajax/get_public_table/$', 'img_ajax_get_public_table', name='img_ajax_get_public_table'),

    url(r'^ajax/assign_group/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully assigned image <b>%(desc)s</b> to group.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('Enter a name of group for image <b>%(desc)s</b>.') % {'desc': desc}),
         'confirmation':         _('Assign to group'),
         'form_class':           AssignGroupForm,
         'request_url_post':     'user/system_image/set_group/',
         'request_url_both':     {'groups': 'user/group/list_groups/'},
         'id_key':               'system_image_id', },
        name='img_ajax_assign_group'),
    url(r'^ajax/revoke_group/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully revoked group\'s assigment.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to make image <b>%(desc)s</b> private?') % {'desc': desc}),
         'request_url':     'user/system_image/set_private/',
         'id_key':          'system_image_id', },
         name='img_ajax_revoke_group'),

    url(r'^ajax/add_image_http/$', 'img_ajax_add_image_http', name='img_ajax_add_image_http'),
    url(r'^ajax/edit_image/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully edited this image.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('Edit image data:') % {'desc': desc}),
         'confirmation':         _('Save'),
         'request_url_get':      'user/system_image/get_by_id/',
         'request_url_post':     'user/system_image/edit/',
         'request_url_both':     {'disk_controllers': 'user/system_image/get_disk_controllers/',
                                  'video_devices':  'user/system_image/get_video_devices/',
                                  'network_devices': 'user/system_image/get_network_devices/', },
         'id_key':               'system_image_id',
         'form_class':           EditImageForm,
        },
        name='img_ajax_edit_image'),

    url(r'^ajax/change_to_storage/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully changed image <b>%(desc)s</b> to a storage disk.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to change image <b>%(desc)s</b> to a storage disk?') % {'desc': desc}),
         'request_url':     'user/system_image/convert_to_storage_image/',
         'id_key':          'system_image_id', },
        name='img_ajax_change_to_storage'),

)


urlpatterns = patterns('',
    url(r'^images/', include(images_patterns)),
)
