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

"""@package src.wi.urls.admin_cm.template

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.template import TemplateForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import form_generic_id, direct_to_template, simple_generic_id, form_generic


template_patterns = patterns('wi.views.admin_cm.template',
    url(r'^templates/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/templates.html'}, name='cma_templates'),
    url(r'^ajax/get_table_templates/$', 'cma_ajax_get_table_templates', name='cma_ajax_get_table_templates'),
    url(r'^ajax/delete_template/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted template <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete template <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_cm/template/delete/',
         'id_key':          'template_id', },
        name='cma_ajax_delete_template'),
    url(r'^ajax/add_template/$', admin_cm_permission(form_generic),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully created a template.') % {'desc': desc}),
         'confirmation':        _('Create'),
         'request_url_post':     'admin_cm/template/add/',
         'form_class':           TemplateForm},
        name='cma_ajax_add_template'),
    url(r'^ajax/edit_template/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully edited selected template.') % {'desc': desc}),
         'confirmation':        _('Save'),
         'request_url_post':    'admin_cm/template/edit/',
         'request_url_get':     'admin_cm/template/get_by_id/',
         'id_key':              'template_id',
         'form_class':           TemplateForm},
        name='cma_ajax_edit_template'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(template_patterns)),
)
