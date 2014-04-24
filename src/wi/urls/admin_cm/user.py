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

"""@package src.wi.urls.admin_cm.user

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.user import ChangeQuotaForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.forms import PasswordForm
from wi.utils.views import form_generic_id, direct_to_template, \
    simple_generic_id


user_patterns = patterns('wi.views.admin_cm.user',
    url(r'^users/$', admin_cm_permission(direct_to_template), {'template_name': 'admin_cm/users.html'}, name='cma_users'),
    url(r'^user_account/(?P<user_id>\d+)/$', 'cma_user_account', name='cma_user_account'),
    url(r'^ajax/get_user_data/(?P<user_id>\d+)/$', 'cma_ajax_get_user_data', name='cma_ajax_get_user_data'),
    url(r'^ajax/get_table_users/$', 'cma_ajax_get_table_users', name='cma_ajax_get_table_users'),
    url(r'^ajax/edit_quota/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully changed the user\'s quota.') % {'desc': desc}),
         'confirmation':        _('Save'),
         'form_class':          ChangeQuotaForm,
         'request_url_post':    'admin_cm/user/change_quota/',
         'request_url_get':     'admin_cm/user/check_quota/',
         'id_key':              'user_id'},
        name='cma_ajax_edit_quota'),
    url(r'^ajax/set_admin/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully promoted user <b>%(desc)s</b> to CM administrator.') % {'desc': desc}),
         'ask_msg':             (lambda desc: _('Do you want to promote user <b>%(desc)s</b> to CM administrator?') % {'desc': desc}),
         'request_url_post':    'admin_cm/admin/add/',
         'id_key':              'user_id',
         'form_class':          PasswordForm},
        name='cma_ajax_set_admin'),
    url(r'^ajax/change_cm_password/$', 'cma_ajax_change_cm_password', name='cma_ajax_change_cm_password'),
    url(r'^ajax/unset_admin/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully demoted administrator <b>%(desc)s</b> to regular user.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to demote administrator <b>%(desc)s</b> to simple user?') % {'desc': desc}),
         'request_url':     'admin_cm/admin/delete/',
         'id_key':          'user_id', },
        name='cma_ajax_unset_admin'),
    url(r'^ajax/change_quota/$', 'cma_ajax_change_quota', name='cma_ajax_change_quota'),

)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(user_patterns)),
)
