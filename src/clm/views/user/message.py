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

"""@package src.clm.views.user.message
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from clm.models.message import Message
from clm.utils.decorators import user_log
from clm.utils.exception import CLMException


@user_log(log=True)
def delete(cm_id, caller_id, message_id):
    """
    Deletes specified Message.

    @clmview_user
    @param_post{message_id,int} id of the message to delete
    """
    m = Message.get(message_id)
    try:
        m.delete()
    except:
        raise CLMException('message_delete')


@user_log(log=False)
def get_list(cm_id, caller_id):
    """
    Returns list of caller's messages.

    @clmview_user
    @response{list(dict)} dicts describing caller's messages
    """
    return [m.dict for m in Message.objects.filter(user_id=caller_id)]
