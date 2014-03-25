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

"""@package src.clm.utils.message
"""

import logging
from common.states import message_levels
from clm.models.message import Message

log = logging.getLogger('clm')


def add(user_id, data):
    """
    Creates new Message described by @prm{param}.
    It's called during error and info Messages' creation.

    @parameter{user_id,int} id if the Message creator
    @parameter{data,dict} Message params
    @dictkey{user_id,int} id if the Message creator
    @dictkey{level,int} level of the Messages
    @dictkey{code} Message's code
    @parameter{params,dict} @asrequired{Message.create(), optional}
    """
    try:
        m = Message.create(data)
        m.save()
        #Session.add(m)
        #Session.commit()
    except:
        log.exception('Add message')


def error(user_id, code, params={}):
    """
    Creates error level message from given @{params}.

    @parameter{user_id,int} id of the Message creator
    @parameter{code,int} Message code (required while rendering from template)
    @parameter{params,dict} @asrequired{add(), optional}
    """
    d = {}
    d['user_id'] = user_id
    d['level'] = message_levels['error']
    d['params'] = params
    d['code'] = code
    add(user_id, d)


def info(user_id, code, params={}):
    """
    Creates info level message from given \c params.

    @parameter{user_id,int} id of the Message creator
    @parameter{code,int} Message code (required while rendering from template)
    @parameter{params,dict} @asrequired{add(), optional}
    """
    d = {}
    d['user_id'] = user_id
    d['level'] = message_levels['info']
    d['params'] = params
    d['code'] = code
    add(user_id, d)
