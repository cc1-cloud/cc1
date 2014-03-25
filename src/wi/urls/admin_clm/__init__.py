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

"""@package src.wi.urls.admin_clm
@author Piotr Wójcik
@date 31.01.2014
"""

from django.conf.urls import patterns, url, include
from wi.utils.decorators import admin_clm_permission
from wi.utils.views import direct_to_template

urlpatterns = patterns('',
                       (r'', include('wi.urls.admin_clm.news')),
                       (r'', include('wi.urls.admin_clm.user')),
                       (r'', include('wi.urls.admin_clm.cm')),
                       url(r'^admin_clm/$', admin_clm_permission(direct_to_template), {'template_name': 'admin_clm/base.html'}, name='admin_clm'),

                      )
