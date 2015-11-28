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

"""@package src.cm.views.ci.storage
@author Maciej Nabozny <mn@mnabozny.pl>
@alldecoratedby{src.cm.utils.decorators.ni_log}
"""

from cm.utils.decorators import ci_log
from cm.models.storage import Storage
from cm.models.node import Node
from common.states import storage_states
from django.template import loader, Context
from cm.utils.exception import CMException


@ci_log(log=True)
def get_list(remote_ip):
    """
    @cmview_ci
    @param_post{remote_ip,string}
    """
    storages = Storage.objects.filter(state=storage_states['ok'])
    return [storage.name for storage in storages]


@ci_log(log=True)
def get_template(remote_ip, name):
    """
    @cmview_ci
    @param_post{remote_ip,string}
    @param_post{name}
    """
    storage = Storage.objects.get(name=name)
    return storage.libvirt_template()


@ci_log(log=True)
def get_images_template(remote_ip):
    """
    @cmview_ci
    @param_post{remote_ip,string}
    """
    try:
        node = Node.objects.get(address=remote_ip)
    except:
        raise CMException('node_not_found')

    template_images = loader.get_template('pools/images.xml')
    template_info = loader.get_template('volumes/file.xml')
    images_pool = template_images.render(Context({'node': node}))
    volume_info = template_info.render(Context({'name': 'info', 'size': 1, 'node': node}))
    return {'images_pool': images_pool, 'volume_info': volume_info}
