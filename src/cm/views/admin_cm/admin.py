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

"""@package src.cm.views.admin_cm.admin


@alldecoratedby{src.cm.utils.decorators.admin_cm_log}
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
"""

from cm.utils.exception import CMException
from cm.utils.decorators import admin_cm_log, guest_log
from cm.models.admin import Admin
from cm.models.user import User

import subprocess

@admin_cm_log(log=True)
def add(caller_id, user_id, new_password):
    """
    Creates new admin of the cluster.

    @cmview_admin_cm
    @param_post{user_id,int} id of the User to gain CM Admin privileges
    @param_post{new_password,string} CM Admin password for User
    """
    # verify if exists an user with the id given (which will become admin)
    try:
        user = User.objects.get(pk=user_id)
    except:
        raise CMException('admin_add')

    admin = Admin()
    admin.user = user
    admin.password = new_password

    try:
        admin.save()
    except:
        raise CMException('admin_add')


@admin_cm_log(log=True)
def delete(caller_id, user_id):
    """
    Removes specified User with id @prm{cmadmin_id} from CM Admins.

    @cmview_admin_cm
    @param_post{user_id,int} id of the User to revoke CM admin privileges
    """

    try:
        admin = Admin.objects.get(pk=user_id)
        admin.delete()
    except:
        raise CMException('admin_delete')


@admin_cm_log(log=True)
def change_password(admin_id, new_password):
    """
    Method to change CM Admin password.

    @cmview_admin_cm
    @param_post{new_password,string} new password to set
    """

    try:
        admin = Admin.objects.get(pk=admin_id)
        admin.password = new_password
        admin.save()
    except:
        raise CMException('admin_change_password')


@admin_cm_log(log=True)
def list_admins(caller_id):
    """
    Method returns list of the CM Admins.

    @cmview_admin_cm
    @response{list(int)} ids of the CM Admins
    """
    admins = []
    for admin in Admin.objects.all():
        admins.append(admin.user.id)
    return admins

@admin_cm_log(log=True)
def restart(caller_id):
    """
    Method returns list of the CM Admins.

    @cmview_admin_cm
    """
    if subprocess.call(['/usr/sbin/cc1_cm_storage', 'mount']) != 0:
        raise CMException('cm_restart')

    if subprocess.call(['/usr/sbin/cc1_cm_node', 'start']) != 0:
        raise CMException('cm_restart')

    if subprocess.call(['/usr/sbin/cc1_cm_monitoring', 'start']) != 0:
        raise CMException('cm_restart')

    if subprocess.call(['/usr/sbin/cc1_cm_vnc', 'start']) != 0:
        raise CMException('cm_restart')


@guest_log(log=True)
def am_i_admin(caller_id):
    """
    @cmview_guest
    @response{bool} True if caller is admin and False if not
    """
    return caller_id in [admin.user.id for admin in Admin.objects.all()]
