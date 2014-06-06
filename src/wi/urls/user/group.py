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

"""@package src.wi.urls.user.group

@author Piotr Wójcik
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.group import GroupForm
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, simple_generic_twoid, \
    simple_generic_id, form_generic, form_generic_id


group_patterns = patterns('wi.views.user.group',
    url(r'^$', user_permission(direct_to_template), {'template_name': 'groups/base.html'}, name='grp_groups'),
    url(r'^list_groups/$', user_permission(direct_to_template), {'template_name': 'groups/show_groups.html'}, name='grp_list'),
    url(r'^my_groups/$', user_permission(direct_to_template), {'template_name': 'groups/my_groups.html'}, name='grp_my_groups'),
    url(r'^details/(?P<group_id>\d+)/$', 'grp_details', name='grp_details'),

    url(r'^ajax/get_table_my/$', 'grp_ajax_get_table_my', name='grp_ajax_get_table_my'),
    url(r'^ajax/grp_details_table/(?P<group_id>\d+)/$', 'grp_ajax_grp_details_table', name='grp_ajax_grp_details_table'),

    url(r'^ajax/grp_delete_user_my/(?P<id1>\d+)/(?P<id2>\d+)/$', user_permission(simple_generic_twoid),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully removed user <b>%(desc)s</b> from this group.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to remove user <b>%(desc)s</b> from this group?') % {'desc': desc}),
         'confirmation':    _('Remove'),
         'request_url':     'user/group/delete_user/',
         'id_key2':          'user_id',
         'id_key':          'group_id', },
        name='grp_ajax_delete_user_my_group'),
    url(r'^ajax/grp_add_user_my/(?P<id1>\d+)/(?P<id2>\d+)/$', user_permission(simple_generic_twoid),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully added user <b>%(desc)s</b> to this group.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to add user <b>%(desc)s</b> to this group?') % {'desc': desc}),
         'confirmation':    _('Add'),
         'request_url':     'user/group/activate_user/',
         'id_key2':          'user_id',
         'id_key':          'group_id', },
        name='grp_ajax_add_user_my_group'),

    url(r'^ajax/grp_change_user_my/(?P<id1>\d+)/(?P<id2>\d+)/$', user_permission(simple_generic_twoid),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully changed group leader to user <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to change group leader to user <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/group/change_owner/',
         'id_key2':          'user_id',
         'id_key':          'group_id', },
        name='grp_ajax_change_user_my_group'),

    url(r'^ajax/send_request/(?P<group_id>\d+)/$', 'grp_ajax_send_request', name='grp_ajax_send_request'),
    url(r'^ajax/cancel_request/(?P<id1>\d+)/(?P<id2>\d+)/$', user_permission(simple_generic_twoid),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully canceled request from user <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to cancel request from user <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/group/delete_user/',
         'id_key2':          'user_id',
         'id_key':          'group_id', },
        name='grp_ajax_cancelrequest'),

    url(r'^ajax/get_table_all/$', 'grp_ajax_get_table_all', name='grp_ajax_get_table_all'),

    url(r'^ajax/delete_my_group/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted this group.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete this group? <br/><b>Note!</b> All images from this group will be set private to their owners.')),
         'request_url':     'user/group/delete/',
         'id_key':          'group_id', },
        name='grp_ajax_delete_my_group'),
    url(r'^ajax/edit_my_group/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully edited selected group.') % {'desc': desc}),
         'confirmation':         _('Save'),
         'request_url_post':    'user/group/edit/',
         'request_url_get':     'user/group/get_by_id/',
         'form_class':           GroupForm,
         'id_key':              'group_id', },
        name='grp_ajax_edit_my_group'),

    url(r'^ajax/add_group/$', user_permission(form_generic),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully created a group.') % {'desc': desc}),
         'confirmation':         _('Create'),
         'request_url_post':     'user/group/create/',
         'form_class':           GroupForm},
        name='grp_ajax_add_group'),
)

urlpatterns = patterns('',
    url(r'^groups/', include(group_patterns)),
)
