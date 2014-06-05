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

"""@package src.clm.models.user_group
"""

from django.db import models
from clm.models.user import User
from clm.models.group import Group


class UserGroup(models.Model):
    """
    @model{USER_GROUP}

    "Many-to-many" relationship between Users and Groups. Each User may belong
    (only once) to any clm.models.group.Group.
    """
    ## User in relation
    user = models.ForeignKey(User)
    ## Group in relation
    group = models.ForeignKey(Group)
    ## Membership status
    status = models.IntegerField()

    class Meta:
        app_label = 'clm'
        unique_together = ("user", "group")

    def __unicode__(self):
        return "Group %d - User %s" % (self.group.name, self.user.login)
