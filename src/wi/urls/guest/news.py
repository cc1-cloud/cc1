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

"""@package src.wi.urls.guest.news

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from wi.utils.views import direct_to_template


news_patterns = patterns('wi.views.guest.news',
    url(r'^$', direct_to_template, {'template_name': 'main/news.html'}, name='mai_news'),
    url(r'^ajax/get_table_news_main/$', 'mai_ajax_get_main_news_table', name='mai_ajax_get_main_news_table'),
    url(r'^ajax/get_table_news/$', 'mai_ajax_get_news_table', name='mai_ajax_get_news_table'),
)

urlpatterns = patterns('',
    url(r'^news/', include(news_patterns)),
)
