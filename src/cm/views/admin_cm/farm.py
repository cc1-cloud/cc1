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

"""@package src.cm.views.admin_cm.farm
@alldecoratedby{src.cm.utils.decorators.admin_cm_log}
@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""

from cm.models.farm import Farm
from cm.models.node import Node
from cm.models.template import Template
from cm.models.user import User
from cm.models.vm import VM
from cm.utils import log
from cm.utils.decorators import admin_cm_log
from cm.utils.exception import CMException
from cm.utils.threads.vm import VMThread
from common.states import vm_states, vnc_states, farm_states, node_states


@admin_cm_log(log=True)
def get_by_id(caller_id, farm_id):
    """
    @cmview_admin_cm
    @param_post{farm_id,int} id of the requested farm
    @response{dict} Farm.dict property of the requested Farm
    """
    return Farm.admin_get(farm_id).dict


@admin_cm_log(log=True)
def destroy(caller_id, farm_ids):
    """
    Destroyes specified Farms. Neither Farm's head nor worker nodes are saved.
    Destroyed Farm cannot be recovered.

    @cmview_admin_cm
    @param_post{farm_ids,list(int)} ids of the Farms to destroy

    @response{list{HTTPResponse}} list of responses for each VM destruction
    """
    farms = []
    for farm_id in farm_ids:
        farms.append(Farm.admin_get(farm_id))
    return Farm.destroy(farms)


@admin_cm_log(log=False)
def get_list(caller_id, user_id):
    """
    Returns list of Farms. Returned Farms belong:
    - either to the User specified by @prm{user_id}
    - or to all Users if no @prm{user_id} is provided.

    @cmview_admin_cm
    @param_post{user_id,list} id of the requested Farm's owner

    @response{list(dict)} Farm.dict property for each Farm
    """
    farms = Farm.objects.exclude(state=farm_states['closed']).order_by('-id')
    if user_id:
        farms = farms.filter(user__id__exact=caller_id)
    return [farm.dict for farm in farms]


@admin_cm_log(log=True)
def save_and_shutdown(caller_id, farm_id, name, description):
    """
    Saves and shutdowns specified Farm's head. Worker nodes are destroyed.

    @cmview_admin_cm
    @param_post{farm_id,int} id of the Farm to save
    @param_post{name,string} name which Farm's head should saved to
    @param_post{description,string} description for newly saved Farm
    """
    farm = Farm.admin_get(farm_id)
    return Farm.save_and_shutdown(farm, name, description)


@admin_cm_log(log=True)
def erase(caller_id, farm_ids):
    """
    Cleanes up after failed Farm. Only admin may erase Farm so that he
    previously may perform some analytics.

    @cmview_admin_cm
    @param_post{farm_ids,list(int)} ids of the Farms to erase
    """
    for fid in farm_ids:
        farm = Farm.admin_get(fid)
        for vm in farm.vms.all():
            VM.erase(vm)

            farm.state = farm_states['closed']
            try:
                farm.save()
            except Exception:
                log.exception('Cannot commit changes.')
