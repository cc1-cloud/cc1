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

"""@package src.wi.urls.admin_clm.cm

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _
from wi.forms.cm import EditCMForm, CreateCMForm
from wi.utils.decorators import admin_clm_permission
from wi.utils.views import direct_to_template, simple_generic_id, \
    form_generic_id, form_generic

cm_patterns = patterns('wi.views.admin_clm.cm',
    url(r'^cms$', admin_clm_permission(direct_to_template), {'template_name': 'admin_clm/cms.html'}, name='clm_cms'),
    url(r'^ajax/get_table_cms/$', 'clm_ajax_get_table_cms', name='clm_ajax_get_table_cms'),
    url(r'^ajax/delete_cm/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted CM <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete CM <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/cluster/delete/',
         'id_key':          'cluster_id'},
        name='clm_ajax_delete_cm'),
    url(r'^ajax/lock_cm/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
         {'template_name':  'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully locked CM <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to lock CM <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/cluster/lock/',
         'id_key':          'cluster_id'},
        name='clm_ajax_lock_cm'),
    url(r'^ajax/unlock_cm/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
         {'template_name':  'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully unlocked CM <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to unlock CM <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/cluster/unlock/',
         'id_key':          'cluster_id'},
        name='clm_ajax_unlock_cm'),
    url(r'^ajax/add_cm/$', admin_clm_permission(form_generic),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully created a CM.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('Note: currently logged user becomes CM administrator.') % {'desc': desc}),
         'confirmation':         _('Create'),
         'request_url_post':     'admin_clm/cluster/add/',
         'form_class':           CreateCMForm},
        name='clm_ajax_add_cm'),
    url(r'^ajax/edit_cm/(?P<id1>\d+)/$', admin_clm_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully edited selected CM.') % {'desc': desc}),
         'confirmation':         _('Save'),
         'request_url_post':     'admin_clm/cluster/edit/',
         'request_url_get':      'admin_clm/cluster/get_by_id/',
         'id_key':               'cluster_id',
         'form_class':           EditCMForm},
        name='clm_ajax_edit_cm'),
)

urlpatterns = patterns('',
    url(r'^admin_clm/', include(cm_patterns)),
)
