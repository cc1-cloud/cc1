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

"""@package src.wi.models.user
@author Piotr Wójcik
@author Przemysław Syktus
@date 21.09.2010
"""

from django.db import models


def parse_user(user):
    """
    Helper function that returns \c User object based on the provided dictionary.

    @parameter{user}
    @returns{User}
    """
    return User(user_id=user['user_id'], firstname=user['first'], lastname=user['last'], username=user['login'],
                password='', email=user['email'], organization=user['organization'], is_active=user['is_active'],
                is_admin_clm=user['is_superuser'], cm_id=user['default_cluster_id'],
                default_cluster_id=user['default_cluster_id'])


class User:
    """
    Class for representation of the interface's users.
    """
    username = models.CharField('username', max_length=30, unique=True)
    firstname = models.CharField('firstname', max_length=60)
    lastname = models.CharField('lastname', max_length=60)
    organization = models.CharField('organization', max_length=60)
    email = models.EmailField('e-mail address', blank=True)
    password = models.CharField('password', max_length=128)
    cm_password = models.CharField('cm_password', max_length=128)
    is_active = models.IntegerField('active', default=0)
    is_admin_clm = models.BooleanField('admin clm', default=False)
    is_admin_cm = models.BooleanField('admin cm', default=False)
    cm_id = models.IntegerField('cm_id', default=0)
    admin_cm_id = models.IntegerField('admin_cm_id', default=0)
    default_cluster_id = models.IntegerField('default_cluster_id', default=0)

    def __init__(self, user_id, cm_id, firstname, lastname, username, organization, password, email, is_active=0,
                 is_admin_clm=False, is_admin_cm=False, default_cluster_id=0):
        self.user_id = user_id
        self.cm_id = cm_id
        self.firstname = firstname
        self.lastname = lastname
        self.organization = organization
        self.username = username
        self.email = email
        self.password = password
        self.cm_password = None
        self.admin_cm_id = None
        self.is_active = is_active
        self.is_admin_clm = is_admin_clm
        self.is_admin_cm = is_admin_cm
        self.default_cluster_id = default_cluster_id

    def __unicode__(self):
        return self.username

    def __str__(self):
        return ' '.join(['user_id=', str(self.user_id), 'username=', self.username, 'cm_id=', str(self.cm_id)])

    def __repr__(self):
        return 'user ' + str(self)

    def set_password(self, password):
        self.password = password
