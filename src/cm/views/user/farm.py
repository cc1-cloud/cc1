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

"""@package src.cm.views.user.farm
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <di.dijo@gmail.com>
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
"""

from cm.models.farm import Farm
from cm.models.node import Node
from cm.models.template import Template
from cm.models.user import User
from cm.models.vm import VM
from cm.utils import log
from cm.utils.decorators import user_log
from cm.utils.exception import CMException
from cm.utils.threads.vm import VMThread
from common.states import farm_states, node_states
from cm.utils import message


@user_log(log=True)
def get_by_id(caller_id, farm_id):
    """
    Returns requested Farm.

    @cmview_user
    @param_post{farm_id,int} id of the requested Farm

    @response{dict} Farm.dict property of the requested Farm
    """
    return Farm.get(caller_id, farm_id).dict


@user_log(log=True)
def create(caller_id, name, description, image_id, head_template_id, worker_template_id, public_ip_id, iso_list, disk_list, vnc, groups, count):
    """
    Method creates new caller's Farm.

    @cmview_user
    @param_post{name,string} Farm's name
    @param_post{description,string}
    @param_post{image_id,int} image for WNs and Head
    @param_post{head_template_id,int} Head's template
    @param_post{worker_template_id,int} Worker Node's template
    @param_post{public_ip_id,int} Worker Node's template
    @param_post{iso_list,list}
    @param_post{disk_list,list}
    @param_post{vnc,list}
    @param_post{groups,list}
    @param_post{count,int} number of Worker Nodes

    @raises{farm_create,CMException}
    """
    user = User.get(caller_id)
    try:
        user.check_points()
    except:
        message.warn(caller_id, 'point_limit', {'used_points': user.used_points, 'point_limit': user.points})

    farm = Farm.create(user=user, name=name, description=description)

    vms = VM.create(user, name=name, description=description, image_id=image_id, template_id=worker_template_id,
                    head_template_id=head_template_id, public_ip_id=public_ip_id, iso_list=iso_list, disk_list=disk_list,
                    vnc=vnc, groups=groups, farm=farm, count=count)

    farm.save()
    for vm in vms:
        vm.farm = farm
        if not vm.is_head():
            # disable autosave
            vm.save_vm = 0
        vm.save()

    try:
        farm.save()
    except Exception:
        log.exception(caller_id, 'farm_create')
        raise CMException('farm_create')

    VMThread(vms[0], 'create').start()
    return [vm.dict for vm in vms]


@user_log(log=True)
def destroy(caller_id, farm_id):
    """
    Destroys specified caller's farm.

    @cmview_user
    @param_post{farm_id,int} destroyed farm's id

    @response @asreturned{src.cm.manager.farm.utils.destroy()}
    """

    return Farm.destroy([Farm.get(caller_id, farm_id)])


@user_log(log=False, pack=False)
def get_list(caller_id):
    """
    Returns list of the caller's farms.

    @cmview_user
    @response{list(dict)} data of the requested Farms
    """
    farms = [farm.dict for farm in Farm.objects.exclude(state=farm_states['closed']).filter(user__id__exact=caller_id).order_by('-id')]

    return farms


@user_log(log=True)
def save_and_shutdown(caller_id, farm_id, name, description):
    """
    Safely saves and shutdowns Farm's Head.

    @cmview_user
    @param_post{farm_id,int}
    @param_post{name,string}
    @param_post{description,string}

    @response{src.cm.manager.farm.utils.save_and_shutdown()}
    """
    farm = Farm.get(caller_id, farm_id)
    if farm.user.id == caller_id:
        return Farm.save_and_shutdown(farm, name, description)
    else:
        raise CMException("farm_save")


@user_log(log=False)
def check_resources(caller_id, count, head_template_id, template_id):
    """
    Checks if there is enough resources to start a farm

    @cmview_user
    @param_post{count,int}
    @param_post{head_template_id,int}
    @param_post{template_id,int}

    @response{Boolean}
    """

    head_template = Template.get(head_template_id)
    wn_template = Template.get(template_id)
    available = 0
    for node in list(Node.objects.filter(state=node_states['ok'])):
        available += node.cpu_free / wn_template.cpu

    resp = False
    if available >= count + 1:
        resp = True

    return resp
