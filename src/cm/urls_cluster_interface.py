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

"""
@package src.cm.urls_ci
@author Maciej Nabozny <mn@mnabozny.pl
"""

from django.conf.urls import patterns, url
from cm.utils.decorators import ci_decorated_functions

from cm.views.ci.storage import *
from cm.views.ci.vm import *
from cm.views.ci.node import *
from cm.views.ci.public_ip import *

global ci_decorated_functions
urlpatterns = patterns('',)

for fun in ci_decorated_functions:
    urlpatterns += patterns('', url(r'^%s/%s/' % (fun.__module__.replace('cm.views.ci.', 'ci.').replace('.', '/'),
                                                  fun.__name__), fun)
    )
