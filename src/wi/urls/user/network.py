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

"""@package src.wi.urls.user.network
@author Piotr Wójcik
@date 19.11.2010
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from wi.forms.network import CreateNetworkForm
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, get_list_generic, \
    simple_generic_id, form_generic

resources_patterns = patterns('wi.views.user.network',

    url(r'^networks/$', user_permission(direct_to_template), {'template_name': 'resources/networks.html'}, name='res_networks'),
    url(r'^ajax/network_table/$', user_permission(get_list_generic),
        {'request_url': 'user/network/list_user_networks/'}, name='res_ajax_get_network_table'),
    url(r'^ajax/add_network/$', user_permission(form_generic),
         {'template_name':       'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully added a network') % {'desc': desc}),
         'confirmation':         _('Create'),
         'form_class':           CreateNetworkForm,
         'request_url_post':     'user/network/request/', },
        name='res_ajax_add_network'),
    url(r'^ajax/release_network/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully released network <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to release network <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/network/release/',
         'id_key':          'network_id', },
        name='res_ajax_release_network'),
)

urlpatterns = patterns('',
    url(r'^resources/', include(resources_patterns)),
)
