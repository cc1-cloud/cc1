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

"""@package src.clm.models.message
@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""

from django.db import models
from clm.models.user import User
import json
from clm.utils.exception import CLMException
from datetime import datetime


class Message(models.Model):
    """
    @model{MESSAGE}

    Message is an entity representing user-targeted communicates. Message has
    its level and content. Web interface renders Message's content based on
    it's code and params.
    """
    ## User whom this Message is targetted to @field
    user = models.ForeignKey(User)
    ## Code of this Message's template @field
    code = models.CharField(max_length=128)
    ## Params to insert into Message template @field
    params = models.CharField(max_length=2048)
    ## Message's creation date @field
    creation_date = models.DateTimeField(default=datetime.now)
    ## Importance level of the message (@seealso{src.common.states.message_levels}) @field
    level = models.IntegerField()

    class Meta:
        app_label = 'clm'

    def __unicode__(self):
        """
        @returns{string} Message id
        """
        return str(self.id)

    @property
    def dict(self):
        """
        @returns{dict} Message's data
        \n fields:
        @dictkey{message_id,int} id of this Message
        @dictkey{params} params of this Message
        @dictkey{creation_date,datetime.datetime} creation date of this Message
        @dictkey{level,int} this Message's importance level importance,
        @seealso{src.common.states.message_levels}
        @dictkey{code,string} short code of the Message (locales translate
        short code into human-readable message, which is filled with data from \c params)
        """
        d = {}
        d['message_id'] = self.id
        d['params'] = json.loads(self.params)
        d['creation_date'] = self.creation_date
        d['level'] = self.level
        d['code'] = self.code
        return d

    @staticmethod
    def get(msg_id):
        """
        @parameter{msg_id,int} id of the requested Message

        @returns{Message} instance of the requested Message

        @raises{message_get,CLMException} no such Message
        """
        try:
            m = Message.objects.get(pk=msg_id)
        except:
            raise CLMException('message_get')

        return m

    @staticmethod
    def create(data):
        """
        @parameter{data,dict}
        \n fields:
        @dictkey{user_id,int} User id of the new messages creator
        @dictkey{level,int} importance level of the new message, @seealso{src.common.states.message_levels}
        @dictkey{code,string} short code of the new message (locales translate
        short code into human-readable message, which is filled with data from \c params)
        @dictkey{params} params to fill Message with (optional)

        Method creates and returns new instance of Message.

        @returns{Message} instance of the newly created Message.
        """
        m = Message()
        m.user_id = data['user_id']
        m.level = data['level']
        m.code = data['code']
        m.params = json.dumps(data.get('params', ''))
        return m
