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

"""@package src.wi.urls.admin_clm.user
@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf import settings
from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _
from wi.forms.user import AccountDataEditAdminCLM
from wi.utils.decorators import admin_clm_permission
from wi.utils.views import direct_to_template, simple_generic_id, \
    form_generic_id, get_list_generic_id

user_patterns = patterns('wi.views.admin_clm.user',

    url(r'^users/$', admin_clm_permission(direct_to_template), {'template_name': 'admin_clm/users.html'}, name='clm_users'),
    url(r'^user_account/(?P<userid>\d+)/$', 'clm_user_account', name='clm_user_account'),
    url(r'^ajax/get_table_users/$', 'clm_ajax_get_table_users', name='clm_ajax_get_table_users'),
    url(r'^ajax/activate_user/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully activated user <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to activate user <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/user/activate/',
         'id_key':          'user_id',
         'param':           {'wi_data': settings.WI_DATA}},
        name='clm_ajax_activate_user'),

    url(r'^ajax/block_user/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully blocked user <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to block user <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/user/block/',
         'id_key':          'user_id',
         'param':           {'block': True, 'wi_data': settings.WI_DATA}},
        name='clm_ajax_block_user'),
    url(r'^ajax/unblock_user/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully unblocked user <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to unblock user <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/user/block/',
         'id_key':          'user_id',
         'param':           {'block': False, 'wi_data': settings.WI_DATA}},
        name='clm_ajax_unblock_user'),

    url(r'^ajax/edit_user_data/(?P<id1>\d+)/$', admin_clm_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('You have successfully changed account data.') % {'desc': desc}),
         'confirmation':         _('Save'),
         'request_url_post':     'admin_clm/user/edit/',
         'request_url_get':      'admin_clm/user/get_by_id/',
         'id_key':               'user_id',
         'form_class':           AccountDataEditAdminCLM},
        name='clm_ajax_edit_user_data'),
    url(r'^ajax/get_user_data/(?P<id1>\d+)/$', admin_clm_permission(get_list_generic_id),
        {'request_url': 'admin_clm/user/get_by_id/',
         'id_key':      'user_id'},
        name='clm_ajax_get_user_data'),
    url(r'^ajax/set_admin/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully changed user <b>%(desc)s</b> to CLM administrator.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to promote user <b>%(desc)s</b> to administrator?') % {'desc': desc}),
         'request_url':     'admin_clm/user/set_admin/',
         'id_key':          'user_id',
         'param':           {'admin': True}},
        name='clm_ajax_set_admin'),
    url(r'^ajax/unset_admin/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully changed <b>%(desc)s</b> to regular user.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to demote administrator <b>%(desc)s</b> to regular user?') % {'desc': desc}),
         'request_url':     'admin_clm/user/set_admin/',
         'id_key':          'user_id',
         'param':           {'admin': False}},
        name='clm_ajax_unset_admin'),
    url(r'^ajax/delete_user/(?P<id1>\d+)/$', admin_clm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully deleted user <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to delete user <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'admin_clm/user/delete/',
         'id_key':          'user_id', },
        name='clm_ajax_delete_user'),
    url(r'^ajax/set_password/(?P<id1>\d+)/$', 'clm_ajax_set_password', name='clm_ajax_set_password'),

)

urlpatterns = patterns('',
    url(r'^admin_clm/', include(user_patterns)),
)
