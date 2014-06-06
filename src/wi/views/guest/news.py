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

"""@package src.wi.views.guest.news

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 17.03.2011
"""

from wi.utils import messages_ajax
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.views import prep_data


@django_view
@ajax_request
def mai_ajax_get_main_news_table(request):
    """
    Ajax view for fetching news list (first 3).
    """
    if request.method == 'GET':
        response = prep_data('guest/news/get_list/', request.session)
        sticky_news = [x for x in response if x['sticky'] == 1][:3]

        return messages_ajax.success(sticky_news)


@django_view
@ajax_request
def mai_ajax_get_news_table(request):
    """
    Ajax view for fetching news list (whole).
    """
    if request.method == 'GET':
        response = prep_data('guest/news/get_list/', request.session)
        return messages_ajax.success(response)
