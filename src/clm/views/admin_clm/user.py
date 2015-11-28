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

"""@package src.clm.views.admin_clm.user

@alldecoratedby{src.clm.utils.decorators.admin_clm_log}
"""

from django.conf import settings as settings
from clm.models.user import User
from clm.models.cluster import Cluster
from clm.utils import mail
from clm.utils.cm import CM
from clm.utils.decorators import admin_clm_log
from clm.utils.exception import CLMException
from common.states import user_active_states
from datetime import datetime
from clm.utils import log


@admin_clm_log(log=True)
def edit(cm_id, caller_id, user_id, first=None, last=None, organization=None, email=None):
    """
    @clmview_admin_clm
    @param_post{user_id,int} id of the user to edit
    @param_post{first,string} new firstname
    @param_post{last,string} new lastname
    @param_post{organization,string} new organization user belong to
    @param_post{email,string} new user's email

    @response{dict} edited User data after update, (User.dict() property)
    """

    user = User.get(user_id)
    if first:
        user.first = first
    if last:
        user.last = last
    if organization:
        user.organization = organization
    if email:
        user.email = email
    try:
        user.save()
    except:
        raise CLMException('user_edit')
    return user.dict


@admin_clm_log(log=False)
def get_by_id(cm_id, caller_id, user_id):
    """
    @clmview_admin_clm
    @param_post{user_id,int}

    @response{dict} requested User data (User.dict() property)
    """
    user = User.get(user_id)
    return user.dict


@admin_clm_log(log=True)
def get_list(cm_id, caller_id):
    """
    @clmview_admin_clm
    @response{list(dict)} dict property for each User
    """
    return [u.dict for u in User.objects.all()]


@admin_clm_log(log=True)
def activate(cm_id, caller_id, user_id, wi_data):
    """
    Activates specified User. Activation may require several actions,
    depending on instructions provided in CLM's config.py file.

    @clmview_admin_clm
    @param_post{user_id,int} id of the User to activate
    @param_post{wi_data,dict} data for confirmation email

    @response{list(dict)} unlocked CMs available for user
    """
    user = User.get(user_id)

    cms = []

    for cluster in Cluster.objects.filter(state__exact=0):
        resp = CM(cluster.id).send_request("guest/user/add/", new_user_id=user.id)

        if resp['status'] == 'ok':
            cms.append(cluster.id)

    user.is_active = user_active_states['ok']
    # don't overwrite activation_date
    if not user.activation_date:
        user.activation_date = datetime.now()

    try:
        user.save()
    except:
        raise CLMException('user_activate')

    if settings.MAILER_ACTIVE:
        mail.send_activation_confirmation_email(user, wi_data)
    return cms


@admin_clm_log(log=True)
def block(cm_id, caller_id, user_id, wi_data, block):
    """
    Block/unblocks User account. User should not and cannot be deleted. For
    technical and legal reasons in order to restrict its access to CC1 Cloud
    it should only be blocked. That way blocked User's data and activities
    stay stored in database. In case of detection of any suspicious / illegal
    activity performed on blocked User's Virtual Machine or using its
    Public IP, that activity may be associated with User account.

    @clmview_admin_clm
    @param_post{user_id,int}
    @param_post{wi_data,dict} fields: 'site_name'
    @param_post{block,bool} whether to block or unblock.
    """
    user = User.get(user_id)

    if block:
        if user.is_active == user_active_states['ok'] or user.is_active == user_active_states['email_confirmed']:
            user.is_active = user_active_states['blocked']
        else:
            raise CLMException('user_state')
    else:
        if user.is_active == user_active_states['blocked']:
            user.is_active = user_active_states['ok']
        else:
            raise CLMException('user_state')

    try:
        user.save()
    except Exception:
        raise CLMException('user_block' if block else 'user_unblock')

    if settings.MAILER_ACTIVE:
        try:
            mail.send_block_email(user, block, wi_data)
        except Exception, e:
            log.error(caller_id, "Cannot send block/unblock email: %s" % str(e))

    return user.dict


@admin_clm_log(log=True)
def set_admin(cm_id, caller_id, user_id, admin):
    """
    Sets/unsets User as CLM admin. CLM admin has an ability to manage Cloud
    Users.

    @clmview_admin_clm
    @param_post{user_id,int} id of the User to set superuser
    @param_post{admin,bool} if True - User becomes admin, if False - User
    loses admin priviledges
    """
    user = User.get(user_id)
    user.is_superuser = admin

    try:
        user.save()
    except Exception:
        raise CLMException('user_set_admin' if admin else 'user_unset_admin')

    return None


@admin_clm_log(log=True)
def delete(cm_id, caller_id, user_id):
    """
    Deletes User. For technical and legal reasons only inactive User may
    be deleted. Other users may only be blocked.

    @clmview_admin_clm
    @param_post{user_id,int} id of the User to delete
    """
    user = User.get(user_id)

    if user.last_login_date or user.is_active == user_active_states['ok']:
        raise CLMException('user_active')

    try:
        user.delete()
    except Exception:
        raise CLMException('user_delete')

    return user.dict


@admin_clm_log(log=True)
def set_password(cm_id, caller_id, user_id, new_password):
    """
    @clmview_admin_clm
    @param_post{user_id,int} User id
    @param_post{new_password,string} new password
    """

    user = User.get(user_id)
    user.password = new_password

    try:
        user.save()
    except Exception:
        raise CLMException('user_edit')

    return user.dict
