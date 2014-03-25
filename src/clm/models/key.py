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

"""@package src.clm.models.key
@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <di.dijo@gmail.com>
"""

from django.db import models
from clm.models.user import User
from datetime import datetime


class Key(models.Model):
    """
    @model{KEY}
    Key is responsible for public RSA key file. CTX mechanizm of CC1 enables
    an injection of such a file.
    """
    ## this Key's owner @field
    user = models.ForeignKey(User)
    ## this Key's human-friendly name @field
    name = models.CharField(max_length=45)
    ## this Key's fingerprint @field
    fingerprint = models.CharField(max_length=47)
    ## content of this Key @field
    data = models.TextField()
    ## creation date @field
    creation_date = models.DateTimeField(default=datetime.now)

    class Meta:
        app_label = 'clm'

    def __unicode__(self):
        """
        @returns name of this Key
        """
        return self.name

    @property
    def dict(self):
        """
        @returns{dict} this Key's data
        \n fields:
        @dictkey{key_id,int} id of this Key
        @dictkey{name,string} this Key's name
        @dictkey{data,string} this Key's content
        @dictkey{fingerprint,string} this Key's fingerprint
        @dictkey{creation_date,datetime.datetime} date when this Key was created
        """
        d = {}
        d['key_id'] = self.id
        d['name'] = self.name
        d['data'] = self.data
        d['fingerprint'] = self.fingerprint
        d['creation_date'] = self.creation_date
        return d
