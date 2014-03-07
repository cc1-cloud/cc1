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

"""@package src.cm.wsgi_ctx
"""

import os

import sys
sys.path.insert(0, '/usr/lib/cc1/')
sys.path.insert(0, '/etc/cc1/cm/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cm.settings_ctx")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
