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

"""@package src.wi.urls.user.user
@author Piotr Wójcik
@date 1.10.2010
"""

from django.conf.urls import patterns, url, include
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, simple_generic, get_list_generic, simple_generic_id

account_patterns = patterns('wi.views.user.user',
    url(r'^$', user_permission(direct_to_template), {'template_name': 'account/base.html'}, name='acc_account'),
    url(r'^account_data/$', user_permission(direct_to_template),
        {'template_name': 'account/account_data.html'}, name='acc_account_data'),

    url(r'^account_data/ajax/get_user_data/$', 'acc_ajax_get_user_data', name='acc_ajax_get_user_data'),

    url(r'^account_data/ajax/edit/$', 'acc_ajax_account_data_edit', name='acc_ajax_account_data_edit'),

    url(r'^account_quotas/$', user_permission(direct_to_template),
        {'template_name': 'account/account_quotas.html'}, name='acc_account_quotas'),
    url(r'^account_data/ajax/get_user_quotas/$', 'acc_ajax_get_user_quotas', name='acc_ajax_get_user_quotas'),

    url(r'^password_change/$', 'acc_password_change', name='acc_password_change'),

    url(r'^ajax/charts/$', user_permission(simple_generic),
        {'template_name': 'account/ajax/charts.html'}, name='acc_ajax_account_charts'),
    url(r'^ajax/charts_points/$', user_permission(get_list_generic),
        {'request_url': 'user/user/points_history/'}, name='acc_ajax_charts_points'),
)

help_patterns = patterns('wi.views.user.user',
    url(r'^form/$', 'hlp_form', name='hlp_form'),
    url(r'^issue_error/$', direct_to_template, {'template_name': 'help/issue_error.html'}, name='hlp_issue_error'),
    url(r'^issue_sent/$', direct_to_template, {'template_name': 'help/issue_sent.html'}, name='hlp_issue_sent'),
)

main_patterns = patterns('wi.views.user.user',
    url(r'^remove_message/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'success_msg':     (lambda desc: _('Message removed.') % {'desc': desc}),
         'request_url':     'user/message/delete/',
         'id_key':          'message_id'},
        name='remove_message'),
    url(r'^get_messages/$', 'get_messages', name='get_messages'),
)

urlpatterns = patterns('',
    url(r'^account/', include(account_patterns)),
    url(r'^help/', include(help_patterns)),
    url(r'^main/', include(main_patterns)),
    url(r'^change_cm/(?P<cm_id>\d+)/$', 'change_cm', name='change_cm'),
)
