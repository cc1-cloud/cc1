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

"""@package src.wi.views.admin_clm.user
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 21.09.2010
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from wi.utils import messages_ajax
from wi.utils.decorators import admin_clm_permission, django_view
from wi.utils.forms import PasswordForm
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import user_active_reversed as user_states
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_clm_permission
def clm_ajax_get_table_users(request):
    """
    Ajax view for fetching users list.
    """
    if request.method == 'GET':
        users = prep_data('admin_clm/user/get_list/', request.session)

        for item in users:
            item['is_activeName'] = unicode(user_states[item['is_active']])

        return messages_ajax.success(users)


@django_view
@admin_clm_permission
def clm_user_account(request, userid, template_name='admin_clm/user_account.html'):
    """
    User account details view.
    """
    return render_to_response(template_name, {'user_id': userid}, context_instance=RequestContext(request))


@django_view
@ajax_request
@admin_clm_permission
@csrf_protect
def clm_ajax_set_password(request, id1, template_name='admin_clm/ajax/set_password.html', form_class=PasswordForm):
    """
    Ajax view for setting user's password.
    """
    id1 = int(id1)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            prep_data(('admin_clm/user/set_password/', {'user_id': id1,
                                                        'new_password': new_password}), request.session)

            if id1 == request.session['user'].user_id:
                request.session['user'].set_password(new_password)
                request.session.modified = True
            return messages_ajax.success(_('You have successfully set password for user <b>%(desc)s</b>.') % {'desc': (force_escape(request.POST.get('desc')))})
    else:
        form = form_class()
    return messages_ajax.success(render_to_string(template_name,
                                                  {'form': form,
                                                   'text': _('Setting password for user <b>%(desc)s</b>:') % {'desc': (force_escape(request.REQUEST.get('desc')))}},
                                                  context_instance=RequestContext(request)),
                                 status=1)
