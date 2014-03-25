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

"""@package src.wi.urls.admin_cm.iso_image
@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.iso_image import EditISOForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import form_generic_id, simple_generic_id, \
    direct_to_template

iso_patterns = patterns('wi.views.admin_cm.iso_image',
    url(r'^iso/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/iso.html'}, name='cma_iso'),
    url(r'^ajax/get_table_iso/$', 'cma_ajax_get_table_iso', name='cma_ajax_get_table_iso'),
    url(r'^ajax/edit_iso/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully edited selected ISO image.') % {'desc': desc}),
         'confirmation':        _('Save'),
         'request_url_both':    {'disk_controllers': 'user/iso_image/get_disk_controllers/'},
         'request_url_post':    'admin_cm/iso_image/edit/',
         'request_url_get':     'admin_cm/iso_image/get_by_id/',
         'id_key':              'iso_image_id',
         'form_class':          EditISOForm,
         },
        name='cma_ajax_edit_iso'),
    url(r'^ajax/delete_iso/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted ISO image <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete ISO image <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/iso_image/delete/',
         'id_key':          'iso_image_id',
         },
        name='cma_ajax_delete_iso'),

    url(r'^ajax/copy_iso/(?P<id1>\d+)/$', 'cma_ajax_copy_iso', name='cma_ajax_copy_iso'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(iso_patterns)),
)
