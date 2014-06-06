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

"""@package src.clm.models.group
@author Maciej Nabożny
"""

from django.db import models
from clm.models.user import User
from clm.utils.exception import CLMException


class Group(models.Model):
    """
    @model{GROUP}

    Group is an entity uniting Users to enable sharing VMImage resources
    between them. Each User may belong to any number of Groups.
    """
    ## User being leader of this Group @field
    leader = models.ForeignKey(User, related_name='group_leader_set')
    ## Human-friendly name of this group @field
    name = models.CharField(max_length=45)
    ## Group's description @field
    desc = models.TextField(null=True, blank=True)
    ## "many-to-many" relationship between Group and User defined through UserGroup @field
    users = models.ManyToManyField(User, through='UserGroup')

    class Meta:
        app_label = 'clm'

    def __unicode__(self):
        """
        @returns{string} name of this Group
        """
        return self.name

    @property
    def dict(self):
        """
        @returns{dict} this Group's data
        \n fields:
        @dictkey{group_id,int} id of this Group
        @dictkey{leader_id,int} id of this Group's leader
        @dictkey{leader_login,string} login of this Group's leader
        @dictkey{leader,string} First name and last name of this Group's leader
        @dictkey{name,string} this Group's name
        @dictkey{description,string} this Group's description
        """
        d = {}
        d['group_id'] = self.id
        d['leader_id'] = self.leader.id or ''
        d['leader_login'] = self.leader.login if self.leader else ''
        d['leader'] = '%s %s' % (self.leader.first, self.leader.last) if self.leader else ''
        d['name'] = self.name
        d['description'] = self.desc
        return d

    @staticmethod
    def get(group_id):
        """
        @parameter{group_id,int} id of the requested Group

        @returns{Group} instance of the requested Group

        @raises{group_get,CLMException} no such Group
        """
        try:
            g = Group.objects.get(pk=group_id)
        except:
            raise CLMException('group_get')

        return g
