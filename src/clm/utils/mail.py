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

"""@package src.clm.utils.mail
@author Piotr Wójcik
@date 3.12.2010
"""


from email.mime.text import MIMEText
from smtplib import SMTPRecipientsRefused
import smtplib

from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _

from clm.models.user import User
from clm.utils import log
from clm.utils.exception import CLMException


def email_error(f):
    """
    Decorator for catching exception with sending emails' error.

    @par Decorated function's declaration
    @code
    @email_error
    function (request, *args, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (request, *arg, **kw)
    @endcode
    """
    def wrap(request, *args, **kwds):
        try:
            return f(request, *args, **kwds)
        except SMTPRecipientsRefused, e:
            error = "%s %s" % (f.__name__, str(e))
            log.error(0, error)
            raise
    return wrap


@email_error
def send(to_address, msg_text, subject):
    """
    @parameter{to_address,string} addressee of the email
    @parameter{msg_text,string} contents of the email
    @parameter{subject,string} subject of the email

    Sends email via STMP server.
    """
    from_address = settings.FROM_EMAIL
    log.debug(0, '%s%s%s%s%s%s%s' % ("send_email(from='", from_address, "', to='", to_address, "', subject='", subject, "')"))

    msg = EmailMessage(subject, msg_text, from_address, [to_address])
    msg.send()


def send_activation_email(activation_key, user, wi_data):
    """
    @parameter{activation_key,string} activation key to be sent
    @parameter{user,string} username of the user to activate
    @parameter{wi_data}

    Sends email with activation key to registred user.
    """
    ctx_dict = {'activation_key': activation_key,
                'site': wi_data['site_domain'],
                'site_name': wi_data['site_name']}

    subject = render_from_template_to_string('registration/activation_email_subject.txt', ctx_dict)
    subject = ''.join(subject.splitlines())
    message = render_from_template_to_string('registration/activation_email.txt', ctx_dict)

    send(user.email, message, subject)


def send_activation_confirmation_email(user, wi_data):
    """
    @parameter{user,string} username of the user to activate
    @parameter{wi_data,dict}, \n fields:
    @dictkey{site_domain,string}
    @dictkey{site_name,string}

    Sends confirmation email to user as admin confirms user's activation.
    """
    ctx_dict = {'site': wi_data['site_domain'],
                'site_name': wi_data['site_name']}
    subject = render_from_template_to_string('admin_clm/activation_email_subject.txt', ctx_dict)
    subject = ''.join(subject.splitlines())
    message = render_from_template_to_string('admin_clm/activation_email.txt', ctx_dict)

    send(user.email, message, subject)


def send_admin_registration_notification(user, wi_data):
    """
    @parameter{user}
    @parameter{wi_data,dict}, \n fields:
    @dictkey{site_name,string}

    Sends notification to admin about a newly registered user.
    """
    ctx_dict = {'site_name': wi_data['site_name']}
    subject = render_from_template_to_string('registration/admin_notify_email_subject.txt', ctx_dict)
    subject = ''.join(subject.splitlines())
    message = render_from_template_to_string('registration/admin_notify_email.txt', user)

    for admin in User.objects.filter(is_superuser=True):
        send(admin.email, message, subject)


def send_reset_password_mail(user, token, wi_data):
    """
    @parameter{user,string} username of the user to reset password
    @parameter{token,string}
    @parameter{wi_data,dict}, \n fields:
    @dictkey{site_domain,string}
    @dictkey{site_name,string}

    Sends mail for password reset.
    """
    ctx_dict = {'site_name': wi_data['site_name'],
                'domain': wi_data['site_domain'],
                'username': user.login,
                'token': token}
    message = render_from_template_to_string('account/password_reset_email.txt', ctx_dict)

    send(user.email, message, _("Password reset on %s") % wi_data['site_name'])


def send_block_email(user, block, wi_data):
    """
    @parameter{user,string} username of the user to reset password
    @parameter{block,boolean} whether to block or unblock.
    @parameter{wi_data,dict}, \n fields:
    @dictkey{site_name,string}
    """
    ctx_dict = {}
    if block:
        send(user.email,
             render_from_template_to_string('account/block_email.txt', ctx_dict),
             _("User account blocked on %s") % wi_data['site_name'])
    else:
        send(user.email,
             render_from_template_to_string('account/unblock_email.txt', ctx_dict),
             _("User account unblocked on %s") % wi_data['site_name'])


def render_from_template_to_string(template_filename, ctx_dict={}):
    """
    @parameter{template_filename,string} path to template of the email
    @parameter{ctx_dict,dict} params to be filled in the email

    Renders strings which can be sent as email contents (basing on template and
    data to be filled in).

    @raises{clm_template_create,CLMException}
    """
    try:
        template = loader.get_template(template_filename)
    except Exception, e:
        log.error(0, "Cannot load template. Error: %s" % str(e))
        raise CLMException('clm_template_create')

    return template.render(Context(ctx_dict))
