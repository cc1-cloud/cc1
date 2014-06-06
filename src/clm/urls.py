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

"""@package src.clm.urls
"""

from django.conf.urls import patterns, include, url
from clm.utils.decorators import decorated_functions

from clm.views.guest.user import *
from clm.views.guest.cluster import *
from clm.views.guest.message import *
from clm.views.guest.news import *

from clm.views.admin_clm.cluster import *
from clm.views.admin_clm.news import *
from clm.views.admin_clm.user import *

from clm.views.admin_cm.user import *
from clm.views.admin_cm.admin import *
from clm.views.admin_cm.cluster import *
from clm.views.admin_cm.farm import *
from clm.views.admin_cm.node import *
from clm.views.admin_cm.storage import *
from clm.views.admin_cm.template import *
from clm.views.admin_cm.vm import *
from clm.views.admin_cm.network import *
from clm.views.admin_cm.iso_image import *
from clm.views.admin_cm.storage_image import *
from clm.views.admin_cm.system_image import *
from clm.views.admin_cm.monia import *
from clm.views.admin_cm.public_ip import *

from clm.views.user.ctx import *
from clm.views.user.group import *
from clm.views.user.iso_image import *
from clm.views.user.storage_image import *
from clm.views.user.system_image import *
from clm.views.user.key import *
from clm.views.user.message import *
from clm.views.user.template import *
from clm.views.user.user import *
from clm.views.user.vm import *
from clm.views.user.farm import *
from clm.views.user.public_ip import *
from clm.views.user.network import *
from clm.views.user.admin import *
from clm.views.user.monia import *

global decorated_functions
urlpatterns = patterns('',)

for fun in decorated_functions:
    urlpatterns += patterns('', url(r'^%s/%s/' % (fun.__module__.replace('clm.views.', '').replace('.', '/'),
                                                  fun.__name__), fun)
    )

# TODO: Remove it when it will be logged somewhere
f = open('/tmp/log-clm', 'w')
for u in urlpatterns:
    f.write(str(u) + '\n')
f.close()
