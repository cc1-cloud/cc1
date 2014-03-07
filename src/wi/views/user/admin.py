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

"""@package src.wi.views.user.admin

@author Piotr Wójcik
@date 31.01.2014
"""

import re

from django.contrib.sites.models import RequestSite
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from wi import settings as wi_settings
from wi.forms.user import CMAuthenticationForm
from wi.utils import REDIRECT_FIELD_NAME
from wi.utils.auth import cm_login, cm_logout
from wi.utils.decorators import django_view, user_permission
from wi.utils.views import prep_data


@django_view
@user_permission
def cma_login(request, template_name='admin_cm/login.html',
              redirect_field_name=REDIRECT_FIELD_NAME,
              authentication_form=CMAuthenticationForm):
    """
    CM panel login page handling.
    """
    rest_data = prep_data({'cms': 'guest/cluster/list_names/'}, request.session)

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == 'POST':
        form = authentication_form(request, data=request.POST, rest_data=rest_data)
        if form.is_valid():
            if not redirect_to or ' ' in redirect_to:
                redirect_to = wi_settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should
            # not be allowed, but things like /view/?param=http://example.com
            # should be allowed. This regex checks if there is a '//' *before*
            # a question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                redirect_to = wi_settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            cm_passwd = form.cleaned_data['password']
            cm_id = form.cleaned_data['cm']

            cm_login(request.session, cm_passwd, cm_id)

            if redirect_to == '/':
                redirect_to = '/admin_cm/'
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request, rest_data=rest_data)

    request.session.set_test_cookie()
    current_site = RequestSite(request)
    return render_to_response(template_name,
                              {'form': form,
                               redirect_field_name: redirect_to,
                               'site': current_site,
                               'site_name': current_site.name,
                            }, context_instance=RequestContext(request))


@django_view
@user_permission
def cma_logout(request, next_page=None,
               template_name='admin_cm/logged_out.html',
               redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Logs out and redirects to the right next page (\c next_page).
    """
    cm_logout(request.session)
    if next_page is None:
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        if redirect_to:
            return HttpResponseRedirect(redirect_to)
        else:
            return render_to_response(template_name,
                                      {'title': _('Logged out')},
                                      context_instance=RequestContext(request))
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page or request.path)
