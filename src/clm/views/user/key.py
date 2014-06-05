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

"""@package src.clm.views.user.key
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

import base64
import hashlib
import os
import re
import subprocess

from clm.models.key import Key
from clm.utils.decorators import user_log
from clm.utils.exception import CLMException


@user_log(log=False)
def get(cm_id, caller_id, name):
    """
    Returns content of the requested Key's. Key must belong to caller.
    @clmview_user

    @parameter{name,string} Key's name

    @response{dict} key's data
    \n fields:
    @dictkey{key_id}
    @dictkey{name}
    @dictkey{data}
    @dictkey{fingerprint}
    @dictkey{creation_date}
    """
    try:
        k = Key.objects.filter(user_id__exact=caller_id).filter(name__exact=name)[0]
    except:
        raise CLMException('ssh_key_get')

    return k.dict


@user_log(log=False)
def get_list(cm_id, caller_id):
    """
    Returns caller's keys.
    @clmview_user

    @response{list(dict)} caller's Keys
    """
    return [k.dict for k in Key.objects.filter(user_id__exact=caller_id)]


@user_log(log=True)
def generate(cm_id, caller_id, name):
    """
    Generates Key pair named @prm{name} for caller.
    @clmview_user

    @parameter{name,string} Key's name

    @response{string} content of private Key's file
    """
    if len(Key.objects.filter(user_id__exact=caller_id)) > 5:  # magic value, keys limit
        raise CLMException('ssh_key_limit')
    if Key.objects.filter(user_id__exact=caller_id).filter(name__exact=name).exists():
        raise CLMException('ssh_key_already_exist')
    if subprocess.call(['ssh-keygen', '-q', '-f', '/tmp/' + str(caller_id) + '_' + name, '-N', '']) != 0:
        raise CLMException('ssh_key_generate')
    f = open('/tmp/' + str(caller_id) + '_' + name, 'r')
    f2 = open('/tmp/' + str(caller_id) + '_' + name + '.pub', 'r')
    k = Key()
    k.user_id = caller_id
    k.data = f2.read()
    k.name = name
    s = hashlib.md5(base64.b64decode(k.data.split()[1])).hexdigest()
    k.fingerprint = ':'.join([s[i:i + 2] for i in xrange(0, 30, 2)])
    try:
        k.save()
    except:
        raise CLMException('ssh_key_generate')
    finally:
        private = f.read()
        os.remove('/tmp/' + str(caller_id) + '_' + name)
        os.remove('/tmp/' + str(caller_id) + '_' + name + '.pub')

    return private


@user_log(log=True)
def add(cm_id, caller_id, key, name):
    """
    Adds given key named @prm{name} with content @prm{key} to caller's keys list.
    @clmview_user

    @parameter{key,string} key's content
    @parameter{name,string} key's name

    @response{None}
    """
    if len(Key.objects.filter(user_id__exact=caller_id)) > 5:  # magic value, keys limit
        raise CLMException('ssh_key_limit')
    k = Key()
    k.user_id = caller_id
    k.data = key
    k.name = name
    r = re.search('ssh-rsa (.*) (.*)', key)
    if not r:
        raise CLMException('ssh_key_format')
    s = hashlib.md5(base64.b64decode(r.groups()[0])).hexdigest()
    k.fingerprint = ':'.join([s[i:i + 2] for i in xrange(0, 30, 2)])
    try:
        k.save()
    except:
        raise CLMException('ssh_key_add')


@user_log(log=True)
def delete(cm_id, caller_id, name):
    """
    Method deletes specified key named @prm{name}.
    @clmview_user

    @parameter{name,string} name of the Key to delete
    @response{None}
    """
    try:
        Key.objects.filter(user_id__exact=caller_id).filter(name__exact=name).delete()
    except:
        raise CLMException('ssh_key_delete')


@user_log(log=True)
def delete_by_id(cm_id, caller_id, key_id):
    """
    Method removes key with id \c id.
    @clmview_user

    @parameter{id,int} id of the key to delete
    @response{None}
    """
    try:
        Key.objects.filter(user_id__exact=caller_id).filter(id__exact=key_id).delete()
    except:
        raise CLMException('ssh_key_delete')
