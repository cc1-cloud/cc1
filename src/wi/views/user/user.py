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

"""@package src.wi.views.user.user

@author Piotr Wójcik
@date 31.01.2014
"""

from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.forms.user import CMAuthenticationForm, HelpForm, PasswordChangeForm, \
    AccountDataEdit
from wi.utils import get_dict_from_list, messages_ajax
from wi.utils.decorators import django_view, user_permission
from wi.utils.exceptions import RestErrorException
from wi.utils.messages_ajax import ajax_request
from wi.utils.messages_codes import get_message
from wi.utils.states import message_levels_reversed
from wi.utils.views import prep_data


@django_view
@user_permission
def change_cm(request, cm_id, success_url='mai_main'):
    """
    View changing used CM.
    """
    request.session['user'].cm_id = int(cm_id)
    request.session.modified = True
    messages.success(request, _('Cluster Manager changed.'))

    return redirect(request.META['HTTP_REFERER'] or success_url)


@django_view
@ajax_request
@user_permission
def get_messages(request):
    """
    Ajax view fetching user messages.
    """
    if request.method == 'POST':
        response = prep_data('user/message/get_list/', request.session)

        for item in response:
            item['text'] = get_message(item['code'], item['params'])
            item['level'] = message_levels_reversed[item['level']]
        return messages_ajax.success(response)


@django_view
@ajax_request
@user_permission
def acc_ajax_get_user_data(request):
    """
    Ajax view. Returns user account data.
    """
    if request.method == 'GET':
        rest_data = prep_data({'user': 'user/user/get_my_data/',
                               'cms': 'guest/cluster/list_names/'
                              }, request.session)
        user_data = rest_data['user']

        users_cm = get_dict_from_list(rest_data['cms'], user_data['default_cluster_id'], key='cluster_id')
        if users_cm is None:
            raise Exception('User\'s default_cluster_id=%d is not a valid CM id.' % user_data['default_cluster_id'])

        user_data['default_cluster_id'] = users_cm['name']
        return messages_ajax.success(user_data)


@django_view
@ajax_request
@user_permission
@csrf_protect
def acc_ajax_account_data_edit(request, template_name='generic/form.html', form_class=AccountDataEdit):
    """
    Ajax view for user account data editing.
    """
    rest_data = prep_data({'cms': 'guest/cluster/list_names/'}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            prep_data({'user': ('user/user/edit/', form.cleaned_data)}, request.session)

            request.session['user'].email = form.cleaned_data['email']
            request.session['user'].default_cluster_id = form.cleaned_data['default_cluster_id']
            request.session.modified = True

            return messages_ajax.success(_('Account data edited.'))
    else:
        form = form_class(data={'email':              request.session['user'].email,
                                'default_cluster_id': request.session['user'].default_cluster_id}, rest_data=rest_data)

    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'text': '',
                                                                  'confirmation': _('Save')},
                                                  context_instance=RequestContext(request)),
                                  status=1)


@django_view
@ajax_request
@user_permission
def acc_ajax_get_user_quotas(request):
    """
    Ajax view for fetching users' quotas.
    """
    if request.method == 'GET':
        quota = prep_data('user/user/check_quota/', request.session)

        quota['memory'] = filesizeformatmb(quota['memory'])
        quota['used_memory'] = filesizeformatmb(quota['used_memory'])
        quota['storage'] = filesizeformatmb(quota['storage'])
        quota['used_storage'] = filesizeformatmb(quota['used_storage'])

        return messages_ajax.success(quota)


@django_view
@csrf_protect
@user_permission
def acc_password_change(request, template_name='account/password_change_form.html', password_change_form=PasswordChangeForm):
    """
    View for password changing (for logged users).
    """
    if request.method == "POST":
        form = password_change_form(user=request.session['user'], data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            try:
                prep_data(('user/user/set_password/', {'new_password': new_password}), request.session)
            except RestErrorException as ex:
                messages.error(request, ex.value)

            request.session['user'].set_password(new_password)
            request.session.modified = True
            return redirect('acc_password_change_done')
    else:
        form = password_change_form(user=request.session['user'])
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))


@django_view
@user_permission
def hlp_form(request, form_class=HelpForm, template_name='help/form.html'):
    """
    View handling help form.
    """
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            topic, issue, email = form.cleaned_data['topic'], form.cleaned_data['issue'], form.cleaned_data['email']

            name = str(request.session.get('user', form.cleaned_data['firstlast']))
            topic += _(' from user:') + name + ', email: ' + email
            dictionary = {'issue': issue,
                          'topic': topic}
            try:
                prep_data(('user/user/send_issue/', dictionary), request.session)
            except Exception:
                return redirect('hlp_issue_error')

            return redirect('hlp_issue_sent')
    else:
        form = form_class()

    rest_data = prep_data('guest/user/is_mailer_active/', request.session)

    return render_to_response(template_name, dict({'form': form}.items() + rest_data.items()),
                              context_instance=RequestContext(request))
