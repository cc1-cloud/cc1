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

"""@package src.wi.views.admin_cm.user
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.02.2012
"""
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from wi.forms.user import MultipleChangeQuotaForm
from wi.utils.decorators import admin_cm_permission
from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.utils import messages_ajax
from wi.utils.decorators import django_view
from wi.utils.forms import PasswordForm
from wi.utils.messages_ajax import ajax_request
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_table_users(request):
    """
    Ajax view for fetching user list.
    """
    if request.method == 'GET':
        rest_data = prep_data({'users': 'admin_cm/user/get_list/',
                               'admins': 'admin_cm/admin/list_admins/'
                              }, request.session)

        for user in rest_data['users']:
            if user['user_id'] in rest_data['admins']:
                user['is_cmadmin'] = True

        return messages_ajax.success(rest_data['users'])


@django_view
@admin_cm_permission
def cma_user_account(request, user_id, template_name='admin_cm/user_account.html'):
    """
    View rendering user account page.
    """
    return render_to_response(template_name, {'user_id': user_id}, context_instance=RequestContext(request))


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_user_data(request, user_id):
    """
    Ajax view for fetching user data and quotas.
    """
    if request.method == 'GET':
        rest_data = prep_data({'user': ('admin_cm/user/get_by_id/', {'user_id': user_id}),
                               'quota': ('admin_cm/user/check_quota/', {'user_id': user_id}),
                              }, request.session)

        quota = rest_data['quota']
        quota['memory'] = filesizeformatmb(quota['memory'])
        quota['used_memory'] = filesizeformatmb(quota['used_memory'])
        quota['storage'] = filesizeformatmb(quota['storage'])
        quota['used_storage'] = filesizeformatmb(quota['used_storage'])

        rest_data['user']['quota'] = quota

        return messages_ajax.success(rest_data['user'])


@django_view
@ajax_request
@admin_cm_permission
@csrf_protect
def cma_ajax_change_cm_password(request, template_name='admin_cm/ajax/change_password.html', form_class=PasswordForm):
    """
    Ajax view for changing logged CM admin password.
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            prep_data(('admin_cm/user/change_password/', {'new_password': form.cleaned_data['new_password']}), request.session)

            request.session['user'].cm_password = form.cleaned_data['new_password']
            request.session.modified = True
            return messages_ajax.success(_('You have successfully changed your CM password.'))
    else:
        form = form_class()
    return messages_ajax.success(render_to_string(template_name, {'form': form},
                                                  context_instance=RequestContext(request)),
                                status=1)


@django_view
@ajax_request
@admin_cm_permission
@csrf_protect
def cma_ajax_change_quota(request, template_name='generic/form.html', form_class=MultipleChangeQuotaForm):
    """
    Ajax view for changing users quota.
    """
    if request.method == 'POST':
        form = form_class(data=request.POST)
        user_list = request.POST.getlist('userids[]')
        if form.is_valid():
            dictionary = {'user_ids': [int(a) for a in user_list]}
            for value, key in form.cleaned_data.items():
                if key is not None:
                    dictionary[value] = key
            prep_data(('admin_cm/user/multiple_change_quota/', dictionary), request.session)

            return messages_ajax.success(_('You have successfully changed quota.'))
    else:
        form = form_class()
        return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                      'confirmation': _('Change'),
                                                                      'text': ''},
                                                   context_instance=RequestContext(request)))
