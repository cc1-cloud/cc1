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

"""@package src.wi.urls.user.key
@author Piotr Wójcik
@date 19.11.2010
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from wi.forms.key import AddKeyForm
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, get_list_generic, \
    simple_generic_id, form_generic


resources_patterns = patterns('wi.views.user.key',

    url(r'^keys/$', user_permission(direct_to_template), {'template_name': 'resources/keys.html'}, name='res_keys'),
    url(r'^key_file/$', 'res_key_file', name='res_key_file'),
    url(r'^ajax/get_table_keys/$', user_permission(get_list_generic),
        {'request_url':     'user/key/get_list/', },
        name='res_ajax_get_table_keys'),
    url(r'^ajax/generate_key/$', 'res_ajax_generate_key', name='res_ajax_generate_key'),
    url(r'^ajax/add_key/$', user_permission(form_generic),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully added a key') % {'desc': desc}),
         'confirmation':        _('Add'),
         'request_url_post':    'user/key/add/',
         'form_class':          AddKeyForm},
        name='res_ajax_add_key'),
    url(r'^ajax/delete_key/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted key <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you really want to delete key <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/key/delete_by_id/',
         'id_key':          'key_id', },
        name='res_ajax_delete_key'),

    )

urlpatterns = patterns('',
    url(r'^resources/', include(resources_patterns)),
)
