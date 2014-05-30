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

"""@package src.wi.urls.admin_cm.system_image

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ungettext, ugettext_lazy as _

from wi.forms.system_image import EditImageForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import generic_multiple_id, form_generic_id, simple_generic_id, \
    direct_to_template


image_patterns = patterns('wi.views.admin_cm.system_image',
    url(r'^images/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/images.html'}, name='cma_images'),
    url(r'^ajax/get_table_images/$', 'cma_ajax_get_table_images', name='cma_ajax_get_table_images'),
    url(r'^ajax/add_image/$', 'cma_ajax_add_image', name='cma_ajax_add_image'),
    url(r'^ajax/edit_image/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully edited selected image.') % {'desc': desc}),
         'confirmation':        _('Save'),
         'form_class':          EditImageForm,
         'request_url_post':    'admin_cm/system_image/edit/',
         'request_url_get':     'admin_cm/system_image/get_by_id/',
         'id_key':              'system_image_id',
         'request_url_both': {'disk_controllers': 'user/system_image/get_disk_controllers/',
                              'video_devices':  'user/system_image/get_video_devices/',
                              'network_devices': 'user/system_image/get_network_devices/'}
        },
        name='cma_ajax_edit_image'),
    url(r'^ajax/delete_image/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted image <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete image <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/system_image/delete/',
         'id_key':          'system_image_id', },
        name='cma_ajax_delete_image'),
    url(r'^ajax/private_image/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully changed type of image <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to make image <b>%(desc)s</b> private?') % {'desc': desc}),
         'request_url':     'admin_cm/system_image/set_private/',
         'id_key':          'system_image_id', },
        name='cma_ajax_private_image'),
    url(r'^ajax/public_image/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully changed type of image <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to make image <b>%(desc)s</b> public?') % {'desc': desc}),
         'request_url':     'admin_cm/system_image/set_public/',
         'id_key':          'system_image_id', },
        name='cma_ajax_public_image'),

    url(r'^ajax/copy_image/(?P<id1>\d+)/$', 'cma_ajax_copy_image', name='cma_ajax_copy_image'),

)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(image_patterns)),
)
