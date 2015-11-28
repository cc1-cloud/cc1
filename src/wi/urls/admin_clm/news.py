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

"""@package src.wi.urls.admin_clm.news

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.news import NewsForm
from wi.utils.decorators import user_permission, admin_clm_permission
from wi.utils.views import form_generic, simple_generic_id


news_patterns = patterns('wi.views.admin_clm.news',
    url(r'^ajax/add_news/$', admin_clm_permission(form_generic),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('News entry added.') % {'desc': desc}),
         'confirmation':         _('Create'),
         'request_url_post':    'admin_clm/news/add/',
         'form_class':           NewsForm},
        name='mai_ajax_add_news'),
    url(r'^ajax/delete_news/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully removed news entry <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete news entry <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/news/delete/',
         'id_key':          'news_id'},
         name='mai_ajax_delete_news'),
    url(r'^ajax/edit_news/(?P<id1>\d+)/$', 'mai_ajax_edit_news', name='mai_ajax_edit_news'),
)

urlpatterns = patterns('',
    url(r'^news/', include(news_patterns)),
)
