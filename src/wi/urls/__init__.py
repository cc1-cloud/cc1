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

"""@package src.wi.urls

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 21.09.2010
"""

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from wi.utils.decorators import user_permission
from wi.utils.views import simple_generic_id, direct_to_template


urlpatterns = patterns('',
    url(r'^$', direct_to_template, {'template_name': 'main/home.html'}, name='mai_main'),
    (r'^favicon\.ico$', RedirectView.as_view(url='media/img/favicon.ico'), 'favicon.ico'),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('wi',), }),

    (r'', include('wi.urls.guest')),
    (r'', include('wi.urls.user')),
    (r'', include('wi.urls.admin_clm')),
    (r'', include('wi.urls.admin_cm')),
)

# if settings.DEBUG:
urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
