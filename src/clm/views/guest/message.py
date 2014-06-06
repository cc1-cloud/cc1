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

"""@package src.clm.views.guest.message
@alldecoratedby{src.clm.utils.decorators.guest_log}
"""

# from common import response
from clm.models.message import Message
from clm.models.user import User
from clm.utils.exception import CLMException
# from clm.database import Session
from clm.utils.decorators import guest_log
# from django.conf import settings as settings
from clm.utils import mail


@guest_log(log=True)
def add(request):
    """
    Adds new message as described by \c data.

    @parameter{data,dict}
    \n fields @asrequired{src.clm.database.entities.message.create()}
    """

    data = request.data

    # if message is about failing call the admin
    if data['code'] in ['farm_create', 'vm_create', 'vm_save', 'vm_destroy']:
        # mail.send(settings.FROM_EMAIL, 'VM failed, do something!', 'VM failed')
        # for admin in Session.query(User).filter(User.is_superuser == True).all():
        for admin in User.objects.filter(is_superuser__gte=1):
            mail.send(admin.email, 'VM failed, do something!', 'VM failed')

    m = Message.create(data)
    try:
        m.save()
    except:
        raise CLMException('message_add')
