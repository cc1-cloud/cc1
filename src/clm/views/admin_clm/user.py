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


@admin_clm_log(log=True)
def edit(cm_id, caller_id, user_id, first, last, organization, email):
    """
    Function for editing user's data.
    @clmview_admin_clm

    @parameter{id,int}
    @parameter{data,dict}
    \n fields:
    @dictkey{user_id,int} id of the user to edit
    @dictkey{first,string} new firstname
    @dictkey{last,string} new lastname
    @dictkey{organization,string} new organization user belong to
    @dictkey{email,string} new user's email

    @response{dict} user new data, fields:
    @dictkey{first} new firstname
    @dictkey{last} new lastname
    @dictkey{organization} new organization user belong to
    @dictkey{email} new user's email
    """

    user = User.get(user_id)
    user.first = first
    user.last = last
    user.organization = organization
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
    @parameter{cm_id,int}
    @parameter{user_id,int}

    @response{dict} info about user with given id
    """
    user = User.get(user_id)
    return user.dict


@admin_clm_log(log=True)
def get_list(cm_id, caller_id):
    """
    @clmview_admin_clm

    @response{list(dict)} dict's describing users
    """
    return [u.dict for u in User.objects.all()]


@admin_clm_log(log=True)
def activate(cm_id, caller_id, user_id, wi_data):
    """
    Activates User in manner specified in settings
    @clmview_admin_clm

    @parameter{user_id,int}
    @parameter{wi_data,dict}

    @response{list(dict)} unlocked CMs
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
    @clmview_admin_clm

    @parameter{wi_data,dict} fields: 'site_name'
    @parameter{block,bool} whether to block or unblock.
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
        mail.send_block_email(user, block, wi_data)

    return user.dict


@admin_clm_log(log=True)
def set_admin(cm_id, caller_id, user_id, admin):
    """
    Sets/unsets User as superuser.
    @clmview_admin_clm

    @parameter{user_id,int} id of the User to set superuser
    @parameter{admin,bool} if true - User becomes admin, if false - User
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

    @parameter{user_id,int} id of the user to delete
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
    Changes User's password.
    @clmview_admin_clm

    @parameter{user_id,int} User id
    @parameter{new_password,string} new password
    """

    user = User.get(user_id)
    user.password = new_password

    try:
        user.save()
    except Exception:
        raise CLMException('user_edit')

    return user.dict
