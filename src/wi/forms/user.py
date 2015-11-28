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

"""@package src.wi.forms.user

@author Krzysztof Danielowski
@date 31.01.2014
"""
import hashlib

from django import forms
from django.utils.translation import ugettext_lazy as _

from common.states import user_active_states
from wi import settings
from wi.recaptcha_django import ReCaptchaField
from wi.utils import parsing
from wi.utils.auth import authenticate, cm_authenticate
from wi.utils.forms import PasswordForm, attrs_dict
from wi.utils.regexp import regexp, regexp_text
from wi.utils.views import make_request
from wi.utils.widgets import SelectWithDisabled


class AuthenticationForm(forms.Form):
    """
    Class for <b>login</b> form.
    """
    username = forms.CharField(max_length=63,
                               label=_('Username'),
                               widget=forms.TextInput(attrs={'tabindex': '1', 'class': 'required'}))
    password = forms.RegexField(regex=regexp['password'],
                                max_length=255,
                                label=_('Password'),
                                widget=forms.PasswordInput(attrs={'tabindex': '2', 'class': 'required'}),
                                error_messages={'invalid': regexp_text['password']})

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled.

        @note
        Note that the \c request (a HttpRequest object) must have set
        a cookie with the key \c TEST_COOKIE_NAME and value \c TEST_COOKIE_VALUE
        before running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Validates the password.
        """
        if not self.cleaned_data.get('password') or not self.cleaned_data.get('username'):
            return None
        self.cleaned_data['password'] = hashlib.sha1(self.cleaned_data['password']).hexdigest()

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        self.user_cache = authenticate(username, password)

        if self.user_cache is None:
            raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
        elif self.user_cache.is_active == user_active_states['inactive']:
            raise forms.ValidationError(_("Account has not been activated yet. Please, click on the activation link in the email sent to you after the registration step."))
        elif self.user_cache.is_active == user_active_states['email_confirmed']:
            raise forms.ValidationError(_("This account is inactive. Please wait for system operator to activate your account."))

        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))

        return self.cleaned_data

    def get_user(self):
        """
        Returns cached user object instance.
        """
        return self.user_cache


class PasswordResetForm(forms.Form):
    """
    Class of the <b>password's reset</b> form.
    """
    email = forms.EmailField(label=_("E-mail"), max_length=255)

    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        """
        email = self.cleaned_data['email']

        rest_data = make_request('guest/user/email_exists/', {'email': email})
        if rest_data['status'] == 'ok' and rest_data['data'] == False:
            raise forms.ValidationError(_('Incorrect email address.'))

        return email


class SetPasswordForm(forms.Form):
    """
    Class of the <b>password edition (doesnt's require giving the previous one)</b> form.
    """
    new_password1 = forms.RegexField(regex=regexp['password'],
                                     max_length=255,
                                     widget=forms.PasswordInput(attrs=dict(attrs_dict)),
                                     label=_("New password"),
                                     error_messages={'invalid': regexp_text['password']})

    new_password2 = forms.RegexField(regex=regexp['password'],
                                     max_length=255,
                                     widget=forms.PasswordInput(attrs=dict(attrs_dict)),
                                     label=_("New password confirmation"),
                                     error_messages={'invalid': regexp_text['password']})

    def clean(self):
        """
        """
        if 'new_password1' in self.cleaned_data and 'new_password2' in self.cleaned_data:
            if self.cleaned_data['new_password1'] != self.cleaned_data['new_password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))

            self.cleaned_data['new_password1'] = hashlib.sha1(self.cleaned_data['new_password1']).hexdigest()
            del self.cleaned_data['new_password2']
        return self.cleaned_data


class RegistrationForm(PasswordForm):
    """
    Form for <b>registering a new user account</b>.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    """
    login = forms.RegexField(regex=regexp['login'],
                             max_length=63,
                             widget=forms.TextInput(attrs=attrs_dict),
                             label=_('Username'),
                             error_messages={'invalid': regexp_text['login']})
    first = forms.CharField(max_length=63,
                            widget=forms.TextInput(attrs=attrs_dict),
                            label=_('First name'))
    last = forms.CharField(max_length=63,
                           widget=forms.TextInput(attrs=attrs_dict),
                           label=_('Last name'))
    organization = forms.CharField(max_length=63,
                                   widget=forms.TextInput(attrs=attrs_dict),
                                   label=_('Organization'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=255)),
                             label=_('Email address'))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields.keyOrder = ['login', 'first', 'last', 'organization', 'email', 'new_password', 'password2']

        if settings.CAPTCHA:
            self.fields['recaptcha'] = ReCaptchaField()

    def clean_login(self):
        """
        Validate that the login is alphanumeric and is not already in use.
        """
        response = make_request('guest/user/exists/', {'login': self.cleaned_data['login']})

        if response['data'] == False:
            return self.cleaned_data['login']
        else:
            raise forms.ValidationError(_("A user with that login already exists."))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the site.
        """
        response = make_request('guest/user/email_exists/', {'email': self.cleaned_data['email']})

        if response['data'] == False:
            return self.cleaned_data['email']
        else:
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))


class AccountDataEdit(forms.Form):
    """
    Class of the <b>user data edition</b> form.
    """
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=255)),
                             label=_('Email address'))

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        try:
            self.old_email = args[0]['email']
        except Exception:
            self.old_email = kwargs['data']['email']
        super(AccountDataEdit, self).__init__(*args, **kwargs)

        self.fields['default_cluster_id'] = forms.ChoiceField(choices=parsing.parse_cm_list(rest_data), label=_('Default CM'))
        self.fields['default_cluster_id'].widget.attrs['class'] = 'medium'

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the site.
        """
        # if same email as current
        if self.old_email == self.cleaned_data['email']:
            return self.cleaned_data['email']

        rest_data = make_request('guest/user/email_exists/', {'email': self.cleaned_data['email']})

        if rest_data['data']:
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        else:
            return self.cleaned_data['email']

    def clean_default_cluster_id(self):
        """
        Cast 'default_cluster_id' to int.
        """
        return int(self.cleaned_data['default_cluster_id'])


class PasswordChangeForm(SetPasswordForm):
    """
    Class of the <b>password edition (requires giving the previous one)</b>
    form.
    """
    old_password = forms.RegexField(regex=regexp['password'],
                                   max_length=255,
                                   widget=forms.PasswordInput,
                                   label=_("Old password"),
                                   error_messages={'invalid': regexp_text['password']})

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        self.cleaned_data['old_password'] = hashlib.sha1(self.cleaned_data['old_password']).hexdigest()
        old_password = self.cleaned_data["old_password"]

        rest_data = make_request('guest/user/check_password/', {'login': self.user.username, 'password': old_password})
        if rest_data['status'] == 'ok' and rest_data['data'] == False:
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password


class HelpForm(forms.Form):
    """
    Form for <b>sending error information/help</b>.
    """
    topic = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=255)),
                            label=_('Topic'))

    firstlast = forms.CharField(max_length=127,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_('First and last name'))

    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=255)),
                             label=_('Your email address'))

    issue = forms.CharField(widget=forms.Textarea(attrs=dict(attrs_dict, rows=5, maxlength=2048)),
                            label=_('Describe your issue'))

    def __init__(self, *args, **kwargs):
        super(HelpForm, self).__init__(*args, **kwargs)


class AccountDataEditAdminCLM(forms.Form):
    """
    Class for <b>user data edition</b> form.
    """
    first = forms.CharField(max_length=63,
                            widget=forms.TextInput(),
                            label=_("First name"),
                            required=False)
    last = forms.CharField(max_length=63,
                           widget=forms.TextInput(),
                           label=_("Last name"),
                           required=False)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(maxlength=255)),
                             label=_("Email address"))
    organization = forms.CharField(max_length=63,
                                   widget=forms.TextInput(),
                                   label=_("Organization"))

    def __init__(self, *args, **kwargs):
        try:
            self.old_email = args[0]['email']
        except Exception:
            self.old_email = kwargs['data']['email']
        super(AccountDataEditAdminCLM, self).__init__(*args, **kwargs)


class CMAuthenticationForm(forms.Form):
    """
    Class for <b>login to CM admin's panel</b> form.
    """
    password = forms.RegexField(regex=regexp['password'],
                               max_length=255,
                               label=_("Password"),
                               widget=forms.PasswordInput(attrs={'tabindex': '1', 'class': 'required'}),
                               error_messages={'invalid': regexp_text['password']})

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        rest_data = kwargs.pop('rest_data')
        super(CMAuthenticationForm, self).__init__(*args, **kwargs)

        self.fields['cm'] = forms.ChoiceField(choices=parsing.parse_cm_list(rest_data),
                                              initial=request.session['user'].default_cluster_id,
                                              widget=SelectWithDisabled(attrs=dict({'class': 'small'})),
                                              label=_("Cluster Manager"))
        self.fields.keyOrder = ['cm', 'password']

    def clean_cm(self):
        """
        Cast 'cm' to int.
        """
        return int(self.cleaned_data['cm'])

    def clean(self):
        """
        Checks cm password.
        """
        self.cleaned_data['password'] = hashlib.sha1(self.cleaned_data['password']).hexdigest()

        password = self.cleaned_data['password']
        cm = self.cleaned_data['cm']

        if password and not cm_authenticate(self.request.session['user'], password, cm):
                raise forms.ValidationError(_('Please enter a correct password. Note that password field is case-sensitive.'))

        return self.cleaned_data


class ChangeQuotaForm(forms.Form):
    """
    Class for <b>quota's change</b> form.
    """
    cpu = forms.IntegerField(label=_("Cpu Total"))
    memory = forms.IntegerField(label=_("Memory Total [MB]"))
    storage = forms.IntegerField(label=_("Storage Total [MB]"))
    public_ip = forms.IntegerField(min_value=0, label=_("Public IPs Total"))
    points = forms.IntegerField(min_value=0, label=_("Points"))


class MultipleChangeQuotaForm(forms.Form):
    """
    Class for <b>quota's change</b> form.
    """
    cpu = forms.IntegerField(label=_("Cpu Total"), required=False)
    memory = forms.IntegerField(label=_("Memory Total [MB]"), required=False)
    storage = forms.IntegerField(label=_("Storage Total [MB]"), required=False)
    public_ip = forms.IntegerField(min_value=0, label=_("Public IPs Total"), required=False)
    points = forms.IntegerField(min_value=0, label=_("Points"), required=False)


class CopyToUserForm(forms.Form):
    """
    Class for <b>moving image</b> form.
    """
    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(CopyToUserForm, self).__init__(*args, **kwargs)
        self.fields['dest_user_id'] = forms.ChoiceField(choices=parsing.parse_cm_users(rest_data),
                                                       initial=0,
                                                       label=_("User"))
