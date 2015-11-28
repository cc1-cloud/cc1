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

"""@package src.wi.views.user.group

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 01.04.2012
"""
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from wi.utils import messages_ajax, parsing
from wi.utils.decorators import django_view
from wi.utils.decorators import user_permission
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import user_groups_states_reversed
from wi.utils.views import prep_data


@django_view
@ajax_request
@user_permission
@csrf_protect
def grp_ajax_send_request(request, group_id, template_name='generic/simple.html'):
    """
    Ajax view for sending group request membership.
    """
    if request.method == 'POST':
        prep_data(('user/group/join_request/', {'group_id': group_id}), request.session)

        return messages_ajax.success(_('You have successfully sent a request.'))
    else:
        return messages_ajax.success(render_to_string(template_name,
                                                   {'confirmation': _('Yes'),
                                                    'text': _('Do you want to send a request?')},
                                                   context_instance=RequestContext(request)))


@django_view
@ajax_request
@user_permission
def grp_ajax_get_table_my(request):
    """
    Ajax view for fetching user's group list.
    """
    if request.method == 'GET':
        rest_data = prep_data({'own_groups': 'user/group/list_own_groups/',
                               'my_groups': 'user/group/list_groups/'}, request.session)

        leader = parsing.parse_own_groups(rest_data)

        for item in rest_data['my_groups']:
            item['amILeader'] = True if item['group_id'] in leader else False

        return messages_ajax.success(rest_data['my_groups'])


@django_view
@ajax_request
@user_permission
def grp_ajax_get_table_all(request):
    """
    Ajax view for fetching all group list.
    """
    if request.method == 'GET':
        all_groups = prep_data('user/group/get_list/', request.session)

        for item in all_groups:
            item['user_statusName'] = unicode(user_groups_states_reversed[item['user_status']])

        return messages_ajax.success(all_groups)


@django_view
@user_permission
def grp_details(request, group_id, template_name='groups/group_details.html'):
    """
    Group details page view.
    """
    rest_data = prep_data({'groups': 'user/group/list_groups/',
                           'group_data': ('user/group/get_by_id/', {'group_id': group_id}),
                          }, request.session)

    group = rest_data['group_data']
    my_groups = parsing.parse_groups_ids(rest_data)

    group['leader_self'] = True if group['leader_id'] == request.session['user'].user_id else False
    group['member'] = True if group['group_id'] in my_groups else False

    return render_to_response(template_name, {'group': group}, context_instance=RequestContext(request))


@django_view
@ajax_request
@user_permission
def grp_ajax_grp_details_table(request, group_id):
    """
    Ajax view for fetching group details.
    """
    if request.method == 'GET':
        user = request.session['user']
        rest_data = prep_data({'group_data': ('user/group/get_by_id/', {'group_id': group_id}),
                               'members': ('user/group/list_members/', {'group_id': group_id}),
                               'requests': ('user/group/list_requests/', {'group_id': group_id})
                              }, request.session)

        leader_id = rest_data['group_data'].get('leader_id')
        leader = True
        if leader_id == '':
            leader = False
        else:
            if int(user.user_id) != int(leader_id):
                leader = False

        for item in rest_data['members']:
            item['request'] = False
            item['leader'] = leader
            item['self'] = True if int(item['user_id']) == int(user.user_id) else False
            item['group_id'] = group_id
        for item in rest_data['requests']:
            item['request'] = True
            item['leader'] = leader
            item['self'] = True if int(item['user_id']) == int(user.user_id) else False
            item['group_id'] = group_id

        return messages_ajax.success([{'name':_('Members:'), 'items': rest_data['members']},
                                      {'name':_('Requests:'), 'items': rest_data['requests']}])
