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

"""@package src.cm.urls
"""

from django.conf.urls import patterns, url
from cm.utils.decorators import decorated_functions

from cm.views.admin_cm.admin import *
from cm.views.admin_cm.node import *
from cm.views.admin_cm.storage import *
from cm.views.admin_cm.template import *
from cm.views.admin_cm.user import *
from cm.views.admin_cm.vm import *
from cm.views.admin_cm.network import *
from cm.views.admin_cm.iso_image import *
from cm.views.admin_cm.storage_image import *
from cm.views.admin_cm.system_image import *
from cm.views.admin_cm.farm import *
from cm.views.admin_cm.monia import *

from cm.views.user.admin import *
from cm.views.user.farm import *
from cm.views.user.system_image import *
from cm.views.user.storage_image import *
from cm.views.user.iso_image import *
from cm.views.user.template import *
from cm.views.user.user import *
from cm.views.user.vm import *
from cm.views.user.public_ip import *
from cm.views.user.network import *

from cm.views.guest.user import *

from cm.views.admin_cm.public_ip import *
from cm.views.user.ctx import *
from cm.views.user.monia import *


global decorated_functions
urlpatterns = patterns('',)

for fun in decorated_functions:
    urlpatterns += patterns('', url(r'^%s/%s/' % (fun.__module__.replace('cm.views.', '').replace('.', '/'),
                                                  fun.__name__), fun)
    )
