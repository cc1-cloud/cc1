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

"""@package src.wi.urls.user.admin

@author Piotr Wójcik
@date 1.10.2010
"""

from django.conf.urls import patterns, url, include


admin_cm_patterns = patterns('wi.views.user.admin',
    url(r'^login/$', 'cma_login', name='cma_login'),
    url(r'^logout/$', 'cma_logout', name='cma_logout'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(admin_cm_patterns)),
)
