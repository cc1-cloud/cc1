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

"""@package src.wi.urls.user.public_ip
@author Piotr Wójcik
@date 19.11.2010
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _

from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, get_list_generic, simple_generic, simple_generic_id


resources_patterns = patterns('wi.views.user.public_ip',

    url(r'^$', user_permission(direct_to_template), {'template_name': 'resources/base.html'}, name='res_resources'),

    url(r'^elastic_ip/$', user_permission(direct_to_template), {'template_name': 'resources/elastic_ip.html'}, name='res_elastic_ip'),
    url(r'^ajax/ips_table/$', user_permission(get_list_generic), {'request_url': 'user/public_ip/get_list/'}, name='res_ajax_get_ips_table'),
    url(r'^ajax/add_ip/$', user_permission(simple_generic),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('New IP address has been added.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to add an IP address?') % {'desc': desc}),
         'request_url':     'user/public_ip/request/',
         },
        name='res_ajax_request_ip'),
    url(r'^ajax/release_ip/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('IP address <b>%(desc)s</b> has been released.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to release IP address <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/public_ip/release/',
         'id_key':          'public_ip_id',
         },
        name='res_ajax_release_ip'),
    )

urlpatterns = patterns('',
    url(r'^resources/', include(resources_patterns)),
)
