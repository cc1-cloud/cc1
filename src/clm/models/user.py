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

"""@package src.clm.models.user
@author Maciej Nabożny <di.dijo@gmail.com>
"""

from django.db import models
from clm.models.cluster import Cluster
from clm.utils.exception import CLMException


class User(models.Model):
    """
    @model{USER}

    CLM User may have access to one or many CMs.
    There's one default CM for each User. Quotas are set per CM, however
    general User data is defined globally in CLM, within this model.
    """
    ## User's first name @field
    first = models.CharField(max_length=63)
    ## User's last name @field
    last = models.CharField(max_length=63)
    ## default Cluster. @field
    default_cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.SET_NULL)

    ## Users's login for authentication (unique) @field
    login = models.CharField(max_length=63, unique=True)
    ## User's password for authentication @field
    password = models.CharField(max_length=255)
    ## User's email (unique) @field
    email = models.CharField(max_length=255, unique=True)
    ## activation key (required only for specific registration types) @field
    act_key = models.CharField(max_length=63, null=True, blank=True)
    ## User's company or organization @field
    organization = models.CharField(max_length=63)

    ## whether User is active and have rights to use the system @field
    is_active = models.IntegerField()
    ## whether User has admin priviledges @field
    is_superuser = models.IntegerField(null=True, blank=True)
    ## whether User has admin priviledges on any CM @field
    is_superuser_cm = models.IntegerField(null=True, blank=True)

    ## @field
    activation_date = models.DateTimeField(null=True, blank=True)
    ## @field
    last_login_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'clm'

    def __unicode__(self):
        """
        @returns{string} User first and last name
        """
        return self.first + ' ' + self.last

    @property
    def dict(self):
        """
        @returns{dict} this User's data
        \n fields:
        @dictkey{user_id,int} id of this User
        @dictkey{first,string} first name
        @dictkey{last,string} last name
        @dictkey{default_cluster_id,int} id of this User's default cluster
        @dictkey{login,string} login
        @dictkey{email,string} email
        @dictkey{act_key,string} activation key's content
        @dictkey{organization,string} organization
        @dictkey{is_active,bool} true for active User
        @dictkey{is_superuser,bool} true for User with admin privilidges
        @dictkey{activation_date,datetime.datetime} activation's date
        @dictkey{last_login_date,datetime.datetime} last login's date
        """
        d = {}
        d['user_id'] = self.id
        d['first'] = self.first
        d['last'] = self.last
        d['default_cluster_id'] = self.default_cluster.id if self.default_cluster else 0
        d['login'] = self.login
        d['email'] = self.email
        d['act_key'] = self.act_key or ''
        d['organization'] = self.organization or ''
        d['is_active'] = self.is_active or 0
        d['is_superuser'] = self.is_superuser or 0
        d['is_superuser_cm'] = self.is_superuser_cm or 0
        d['activation_date'] = self.activation_date or ''
        d['last_login_date'] = self.last_login_date or ''
        return d

    @property
    def short_dict(self):
        """
        @returns{dict} very short version of User's data
        \n fields:
        @dictkey{user_id,int} id of this User
        @dictkey{first,string} first name
        @dictkey{last,string} last name
        """
        d = {}
        d['user_id'] = self.id
        d['first'] = self.first
        d['last'] = self.last

        return d

    @property
    def own_groups(self):
        """
        @returns{Group queryset} all instances of the groups this User is leader of
        """
        return self.group_leader_set.all()

    @staticmethod
    def get(user_id):
        """
        @parameter{user_id,int} primary index of the User

        @returns{User} instance of requested User

        @raises{user_get,CLMException}
        """
        try:
            u = User.objects.get(pk=user_id)
        except:
            raise CLMException('user_get')
        return u

    @staticmethod
    def is_leader(user_id, group_id):
        """
        @parameter{user_id,int} User's id
        @parameter{group_id,int} Group's id

        @returns{bool} True if User is the Group's leader

        @raises{user_permission,CLMException} User isn't the leader of the given Group
        """

        user = User.get(user_id)

        if user.group_leader_set.filter(id__exact=group_id).exists():
            return True
        else:
            raise CLMException('user_permission')

    @staticmethod
    def superuser(user_id):
        """
        @parameter{user_id,int} User's id

        @returns{bool}
        @avail{True} - User is superuser

        @raises{user_permission,CLMException} User isn't superuser
        """
        user = User.get(user_id)
        if not user.is_superuser:
            raise CLMException('user_permission')
        return True
