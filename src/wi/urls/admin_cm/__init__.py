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

"""@package src.wi.urls.admin_cm

@author Piotr Wójcik
@date 31.01.2014
"""

from django.conf.urls import patterns, url, include

from wi.utils.decorators import admin_cm_permission
from wi.utils.views import direct_to_template, simple_generic


urlpatterns = patterns('',
    url(r'^admin_cm/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/base.html'}, name='cma_admin'),
    url(r'^ajax/move_database/$', admin_cm_permission(simple_generic),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully moved data to archival database.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to move data to archival database?') % {'desc': desc}),
         'request_url':     'admin_cm/history/move/', },
        name='cma_ajax_move_database'),

    (r'', include('wi.urls.admin_cm.cm')),
    (r'', include('wi.urls.admin_cm.vm')),
    (r'', include('wi.urls.admin_cm.farm')),
    (r'', include('wi.urls.admin_cm.iso_image')),
    (r'', include('wi.urls.admin_cm.storage_image')),
    (r'', include('wi.urls.admin_cm.system_image')),
    (r'', include('wi.urls.admin_cm.network')),
    (r'', include('wi.urls.admin_cm.node')),
    (r'', include('wi.urls.admin_cm.storage')),
    (r'', include('wi.urls.admin_cm.user')),
    (r'', include('wi.urls.admin_cm.template')),
)
