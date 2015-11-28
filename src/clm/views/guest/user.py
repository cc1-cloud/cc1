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

"""@package src.clm.views.guest.user
@author Gaetano
@date May 14, 2013
@alldecoratedby{src.clm.utils.decorators.guest_log}
"""

from datetime import datetime
import random
from smtplib import SMTPRecipientsRefused
import string

from django.conf import settings
from django.utils.http import int_to_base36

from clm.models.cluster import Cluster
from clm.models.user import User
from clm.utils import mail
from clm.utils.cm import CM
from clm.utils.decorators import guest_log
from clm.utils.exception import CLMException
from clm.utils.tokens import default_token_generator as token_generator
from common.signature import Signature
from common.states import user_active_states, registration_states, \
    cluster_states


@guest_log(log=False)
def check_password(login, password):
    """
    Checks User password's correctness.

    @clmview_guest
    @param_post{login} user's login
    @param_post{password} password to check

    @response{bool} False if password isn't correct
    @response{dict} User.dict() property if password is correct
    """
    try:
        user = User.objects.get(login=login)
    except User.DoesNotExist:
        raise CLMException('user_get')

    if user.is_active == user_active_states['ok']:
        try:
            user.last_login_date = datetime.now()
            user.save()
        except:
            raise CLMException('user_edit')
    else:
        return False

    if user.password == password:
        return user.dict
    else:
        return False


@guest_log(log=True)
def check_signature(parameters):
    """
    Authenticate S3 request by checking parameters passed by EC2

    @clmview_guest
    @param_post{parameters} dict with all S3 request headers
    """

    try:
        auth_header = parameters['authorization']
        space = auth_header.index(' ')
        auth_header = auth_header[space + 1:]
        login_and_signature = auth_header.split(':')

        login = login_and_signature[0]
        user_signature = login_and_signature[1]

        user = User.objects.get(login=login)
    except User.DoesNotExist, error:
        print 'ERROR', error
        raise CLMException('user_get')
    except KeyError:
        raise CLMException('user_parameter')

    if not Signature.checkSignature(user.password, user_signature, parameters):
        raise CLMException('user_get')
    return True


@guest_log(log=True)
def register(first, last, login, email, new_password, organization, wi_data):
    """
    Registers new user.

    @clmview_guest
    @param_post{first,string} firstname to set
    @param_post{last,string} lastname to set
    @param_post{login,string} login to set
    @param_post{email,string} email to set
    @param_post{new_password,string} password to set
    @param_post{organization,string} organization to set
    @param_post{wi_data,dict} data for sending mail

    @response{dict}
    @dictkey{user,dict} user's data (User.dict() property)
    @dictkey{registration_state,int} state of reqistration @seealso{common.states.registration_state}
    """

    user = User()
    user.first = first
    user.last = last
    try:
        default_cluster_id = Cluster.objects.filter(state=cluster_states['ok'])[0].id
    except:
        default_cluster_id = None

    user.default_cluster_id = default_cluster_id
    user.login = login
    user.email = email
    user.password = new_password
    user.organization = organization
    user.act_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for n in range(40))
    user.is_active = user_active_states['inactive']

    try:
        user.save()
    except:
        raise CLMException('user_register')

    reg_state = -1
    if settings.MAILER_ACTIVE:
        try:
            # mail the user
            mail.send_activation_email(user.act_key, user, wi_data)
        except SMTPRecipientsRefused:
            reg_state = registration_states['error']
        reg_state = registration_states['mail_confirmation']
    else:
        if settings.AUTOACTIVATION:
            # add user to all unlocked CMs while activating
            for cluster in Cluster.objects.filter(state__exact=0):
                # TODO: func user/user is not in cm! so i use guest/user
                resp = CM(cluster.id).send_request("guest/user/add/", new_user_id=user.id)
                if resp['status'] != 'ok':
                    raise CLMException('cm_get')

            user.is_active = user_active_states['ok']
            user.activation_date = datetime.now()
            user.act_key = ''

            reg_state = registration_states['completed']
        else:
            user.is_active = user_active_states['email_confirmed']

            reg_state = registration_states['admin_confirmation']

        try:
            user.save()
        except:
            raise CLMException('user_activate')

    return {'user': user.dict, 'registration_state': reg_state}


@guest_log(log=False)
def exists(login):
    """
    Method check, whether specified @prm{login} already exists.

    @clmview_guest
    @param_post{login,string}

    @response{bool) True if @prm{login} is registered
    @response{bool) False if @prm{login} isn't registered
    """
    return User.objects.filter(login=login).exists()


@guest_log(log=False)
def email_exists(email):
    """
    Method checks, whether user with specified @prm{email} already exists.

    @clmview_guest
    @param_post{email,string}

    @response{bool) True if @prm{email} is registered
    @response{bool) False if @prm{email} isn't registered
    """
    return User.objects.filter(email__exact=email).exists()


@guest_log(log=True)
def activate(act_key, wi_data):
    """
    Method activates User with activation key @prm{act_key}.

    @clmview_guest
    @param_post{act_key,string}
    @param_post{wi_data,string} data for email

    @response{dict} user's data, fields:
    @dictkey{user,dict}
    @dictkey{registration_state,dict}
    """
    try:
        user = User.objects.get(act_key=act_key)
    except:
        raise CLMException('user_get')
    user.is_active = user_active_states['email_confirmed']
    reg_state = registration_states['admin_confirmation']
    if settings.AUTOACTIVATION:
        # add user to all unlocked CMs while activating
        for cluster in Cluster.objects.filter(state__exact=0):
            # TODO: func user/user is not in cm! so i use guest/user
            resp = CM(cluster.id).send_request("guest/user/add/", new_user_id=user.id)
            if resp['status'] != 'ok':
                raise CLMException('cm_get')

        user.is_active = user_active_states['ok']
        reg_state = registration_states['completed']

    user.activation_date = datetime.now()
    user.act_key = ''
    try:
        user.save()
    except:
        raise CLMException('user_activate')

    if settings.MAILER_ACTIVE and reg_state == registration_states['admin_confirmation']:
        try:
            mail.send_admin_registration_notification(user, wi_data)
        except SMTPRecipientsRefused:
            pass

    return {'user': user.dict, 'registration_state': reg_state}


@guest_log(log=True)
def is_mailer_active():
    """
    Info, whether mailer is active

    @clmview_guest
    @response{dict} fiedls:
    @dictkey{mailer_active}
    @dictkey{contact_email}
    """
    return {'mailer_active': settings.MAILER_ACTIVE, 'contact_email': settings.CONTACT_EMAIL}


@guest_log(log=True)
def reset_password_mail(email, wi_data):
    """
    Sends mail for reseting password

    @clmview_guest
    @param_post{email,string} whom send "reset password" mail to
    @param_post{wi_data,dict} fields:
    @dictkey{site_domain}
    @dictkey{site_name}
    """
    if settings.MAILER_ACTIVE:
        user = User.objects.get(email=email)
        token = token_generator.make_token(user)
        try:
            mail.send_reset_password_mail(user, token, wi_data)
            return
        except SMTPRecipientsRefused:
            raise CLMException('reset_password_smtp_error')
    raise CLMException('reset_password_error')


@guest_log(log=True)
def check_token(user_id, token):
    """
    Check password-reset token correctness for User.

    @clmview_guest
    @param_post{user_id} User whose token should be checked
    @param_post{token} token to check

    @response None
    """
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        raise CLMException('user_get')

    if token_generator.check_token(user, int_to_base36(user_id) + u'-' + token):
        return
    raise CLMException('user_bad_token')


@guest_log(log=True)
def set_password_token(user_id, token, new_password):
    """
    Sets new password provided reset-password token is correct.

    @clmview_guest
    @param_post{user_id} id of the User whose password should be set
    @param_post{token} token to set password
    @param_post{new_password,string} new password

    @response{dict} User's new data (if succeeded)
    """
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        raise CLMException('user_get')

    if token_generator.check_token(user, int_to_base36(user_id) + u'-' + token):
        user.password = new_password
        try:
            user.save()
        except Exception:
            raise CLMException('user_set_password')
    else:
        raise CLMException('user_bad_token')
    return user.dict
