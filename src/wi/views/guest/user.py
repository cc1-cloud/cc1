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

"""@package src.wi.views.guest.user

@author Piotr Wójcik
@date 1.10.2010
"""

import re

from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from common.states import registration_states
from wi.forms.user import AuthenticationForm, SetPasswordForm, \
    PasswordResetForm, RegistrationForm
from wi.utils import REDIRECT_FIELD_NAME
from wi.utils.decorators import django_view
from wi.utils.registration import register, activate
from wi.utils.views import prep_data


@django_view
@csrf_protect
@never_cache
def login(request, template_name='auth/login.html', redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """
    Login page handling.
    """

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == 'POST':
        form = authentication_form(data=request.POST)
        if form.is_valid():
            from wi.utils.auth import login as auth_login

            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should
            # not be allowed, but things like /view/?param=http://example.com
            # should be allowed. This regex checks if there is a '//' *before*
            # a question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            user = form.get_user()
            user.set_password(form.cleaned_data['password'])
            auth_login(request, user)

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    if ('user' in request.session):
        return HttpResponseRedirect(reverse('mai_main'))

    request.session.set_test_cookie()
    current_site = RequestSite(request)
    return render_to_response(template_name,
                              {'form': form,
                                redirect_field_name: redirect_to,
                                'site': current_site,
                                'site_name': current_site.name,
                               }, context_instance=RequestContext(request))


@django_view
def logout(request, next_page=None, template_name='auth/logged_out.html', redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Logout and redirection to the right next page (\c next_page).
    """
    from wi.utils.auth import logout as auth_logout
    auth_logout(request.session)
    if next_page is None:
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        if redirect_to:
            return HttpResponseRedirect(redirect_to)
        else:
            return render_to_response(template_name, {'title': _('Logged out')}, context_instance=RequestContext(request))
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page or request.path)


@django_view
@csrf_protect
def acc_password_reset(request, template_name='account/password_reset_form.html', password_reset_form=PasswordResetForm):
    """
    <b>Password reset</b> form handling (email is sent).

    @parameter{request}
    @parameter{template_name} optional
    @parameter{password_reset_form} optional
    """
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            try:
                dictionary = {'email': form.cleaned_data['email'], 'wi_data': settings.WI_DATA}
                prep_data(('guest/user/reset_password_mail/', dictionary), request.session)
            except Exception:
                return redirect('acc_password_reset_error')

            return redirect('acc_password_reset_done')
    else:
        form = password_reset_form()

    rest_data = prep_data('guest/user/is_mailer_active/', request.session)

    return render_to_response(template_name, dict({'form': form}.items() + rest_data.items()),
                              context_instance=RequestContext(request))


# Doesn't need csrf_protect since no-one can guess the URL
@django_view
def acc_password_reset_confirm(request, uidb36=None, token=None,
                               template_name='account/password_reset_confirm.html',
                               form_class=SetPasswordForm):
    """
    Check whether given address hash is correct. Displayes <b>password edition</b> form.

    @code
    acc_password_reset_confirm(request,
                            uidb36=None,
                            token=None,
                            template_name='account/password_reset_confirm.html',
                            form_class=SetPasswordForm)
    @endcode

    @parameter{request}
    @parameter{uidb36} optional
    @parameter{token} optional
    @parameter{template_name} optional
    @parameter{form_class} optional
    """
    assert uidb36 is not None and token is not None  # checked by URLconf
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            dictionary = {'user_id': uid_int, 'token': token, 'new_password': form.cleaned_data['new_password1']}
            try:
                prep_data(('guest/user/set_password_token/', dictionary), request.session)
            except Exception:
                return redirect('acc_password_reset_error_token')

            return redirect('acc_password_reset_complete')
    else:
        try:
            prep_data(('guest/user/check_token/', {'user_id': uid_int, 'token': token}), request.session)
        except Exception:
            return redirect('acc_password_reset_error_token')
        form = form_class()

    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))


@django_view
def hlp_help(request, template_name='help/base.html'):
    """
    Help main page.
    """
    rest_data = prep_data('guest/user/is_mailer_active/', request.session)
    return render_to_response(template_name, rest_data, context_instance=RequestContext(request))


@django_view
def change_language(request, lang, success_url='mai_main'):
    """
    View changing page language.
    """
    request.session['django_language'] = lang
    request.session['_language'] = lang
    request.session.modified = True

    return redirect(request.META['HTTP_REFERER'] or success_url)


@django_view
def reg_register(request, form_class=RegistrationForm, template_name='registration/registration_form.html'):
    """
    Registration form's handling.
    """
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            response = register(**form.cleaned_data)

            if response['status'] != 'ok':
                import logging
                wi_logger = logging.getLogger('wi_logger')
                wi_logger.error('Registration error: %s' % response['status'])
                wi_logger.error(response['data'])

                return redirect('registration_error')

            if response['data']['registration_state'] == registration_states['completed']:
                return redirect('registration_completed')

            if response['data']['registration_state'] == registration_states['mail_confirmation']:
                return redirect('registration_mail_confirmation')

            if response['data']['registration_state'] == registration_states['admin_confirmation']:
                return redirect('registration_admin_confirmation')
    else:
        form = form_class()

    return render_to_response(template_name, {'form': form}, RequestContext(request))


@django_view
def reg_activate(request, **kwargs):
    """
    User's email address's confirmation (by entering the HTTP address provided in email message).
    """
    act_response = activate(**kwargs)
    if act_response:
        if act_response['data']['registration_state'] == registration_states['completed']:
            return redirect('activation_completed')

        if act_response['data']['registration_state'] == registration_states['admin_confirmation']:
            return redirect('activation_admin_confirmation')

    return redirect('activation_error')
