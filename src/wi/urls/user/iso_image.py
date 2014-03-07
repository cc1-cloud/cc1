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

"""@package src.wi.urls.user.iso_image
@author Piotr Wójcik
@date 19.11.2010
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from wi.forms.iso_image import EditISOForm
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, simple_generic_id, \
    form_generic_id


resources_patterns = patterns('wi.views.user.iso_image',

    url(r'^iso/$', user_permission(direct_to_template), {'template_name': 'resources/iso.html'}, name='res_iso'),
    url(r'^ajax/iso_table/$', 'res_ajax_get_iso_table', name='res_ajax_get_iso_table'),
    url(r'^ajax/upload_iso_http/$', 'res_ajax_upload_iso_http', name='res_ajax_upload_iso_http'),
    url(r'^ajax/edit_iso/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('ISO image data edited.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('Edit ISO image data:') % {'desc': desc}),
         'confirmation':         _('Save'),
         'request_url_post':     'user/iso_image/edit/',
         'request_url_get':      'user/iso_image/get_by_id/',
         'request_url_both':     {'disk_controllers': 'user/iso_image/get_disk_controllers/'},
         'id_key':               'iso_image_id',
         'form_class':           EditISOForm},
        name='res_ajax_edit_iso'),
    url(r'^ajax/delete_iso/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully removed ISO image <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you really want to delete ISO image <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/iso_image/delete/',
         'id_key':          'iso_image_id', },
        name='res_ajax_delete_iso'),
)

urlpatterns = patterns('',
    url(r'^resources/', include(resources_patterns)),
)
