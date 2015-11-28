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

"""@package src.cm.views.admin_cm.vm
@alldecoratedby{src.cm.utils.decorators.admin_cm_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <di.dijo@gmail.com>
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
"""

from common.states import vm_states
from cm.utils.decorators import admin_cm_log
from cm.utils.exception import CMException
from cm.models.user import User
from cm.models.vm import VM
from cm.utils.threads.vm import VMThread


@admin_cm_log(log=True)
def create(caller_id, name, description, image_id, template_id, public_ip_id, iso_list, disk_list, vnc, node_id):
    """
    Creates new VM with specified attributes.

    @cmview_admin_cm
    @param_post{name,string}
    @param_post{description,string}
    @param_post{image_id,int}
    @param_post{template_id,int}
    @param_post{public_ip_id,int}
    @param_post{iso_list,list(int)}
    @param_post{disk_list,list(int)}
    @param_post{vnc}
    @param_post{node_id}
    """
    user = User.get(caller_id)
    vms = VM.create(user, name=name, description=description, image_id=image_id,
                    template_id=template_id, public_ip_id=public_ip_id, iso_list=iso_list, disk_list=disk_list,
                    vnc=vnc, groups=[], node_id=node_id)
    for vm in vms:
        thread = VMThread(vm, 'create')
        thread.start()

    return [vm.dict for vm in vms]


@admin_cm_log(log=True)
def destroy(caller_id, vm_id_list):
    """
    Destroyes specified VMs. Destroyed VM can in no way be recovered.

    @cmview_admin_cm
    @param_post{vm_id_list,list} ids to destroy

    @response{src.cm.views.utils.image.destroy()}
    """

    vms = []
    for vm_id in vm_id_list:
        vms.append(VM.admin_get(vm_id))
    return VM.destroy(vms)


@admin_cm_log(log=True)
def erase(caller_id, vm_id_list):
    """
    Cleans up after each of the specified VMs. Erase should be called for
    failed machines after the inspection of the failure.

    @cmview_admin_cm
    @param_post{vm_id_list,list} list of VM id's
    """

    for vm_id in vm_id_list:
        vm = VM.admin_get(vm_id)
        VM.erase(vm)


@admin_cm_log(log=True)
def save_and_shutdown(caller_id, vm_id, name, description):
    """
    Saves and shutdowns specified VM, without checking User quota.

    @cmview_admin_cm
    @param_post{vm_id,string} id of the VM to save
    @param_post{name,string}
    @param_post{description,string}
    """

    vm = VM.admin_get(vm_id)
    user = User.get(vm.user.id)

    if user.used_storage + vm.system_image.size > user.storage:
        raise CMException('user_storage_limit')

    VM.save_and_shutdown(user.id, vm, name, description)


@admin_cm_log(log=False)
def get_list(caller_id, user_id):
    """
    Returns list of VMs that are neither closed nor erased. If user_id is
    provided, only VMs belonging to that user are returned.

    @cmview_admin_cm
    @param_post{user_id,int}

    @response{dict} VM.long_dict property of each VM
    """

    vms = VM.objects.exclude(state__in=[vm_states['closed'], vm_states['erased']]).order_by('-id')

    # if parameter all is false, 'user_id' parameter have to be sent
    if user_id:
        vms = vms.filter(user__id__exact=user_id)

    return [vm.long_dict for vm in vms]


@admin_cm_log(log=False)
def get_by_id(caller_id, vm_id):
    """
    @cmview_admin_cm
    @param_post{vm_id} id of the requested VM

    @response{dict} VM with id @prm{id}
    """
    vm = VM.admin_get(vm_id)
    vm_mod = vm.long_dict
    return vm_mod


@admin_cm_log(log=True)
def restart(caller_id, vm_id_list):
    """
    Sends signal to reboot specified VMs. VM is not saved to SystemImage
    during reboot.

    @cmview_admin_cm
    @param_post{vm_id_list,(list(int))} ids of the VMs to restart
    """

    return VM.restart(vm_id_list)


# Change vm parameters
@admin_cm_log(log=True)
def edit(caller_id, vm_id, name, description):
    """
    Updates VM attributes.

    @cmview_admin_cm
    @param_post{vm_id}
    @param_post{name} (optional) new VM name
    @param_post{description} (optional) new VM description

    @response{src.cm.views.utils.vm.edit()}
    """

    vm = VM.admin_get(vm_id)

    vm.name = name
    vm.description = description
    vm.save()


@admin_cm_log(log=True)
def attach_vnc(caller_id, vm_id):
    """
    Attaches VNC redirection to VM.

    @cmview_admin_cm
    @param_post{vm_id,int} id of the VM to have attached VM redirection
    """
    vm = VM.admin_get(vm_id)
    vm.attach_vnc()

    try:
        vm.save()
    except:
        raise CMException('vnc_attach')


@admin_cm_log(log=True)
def detach_vnc(caller_id, vm_id):
    """
    Detaches VNC redirection from VM.

    @cmview_admin_cm
    @param_post{vm_id,int} id of the VM to have detached VM redirection
    """
    vm = VM.admin_get(vm_id)
    vm.detach_vnc()

    try:
        vm.save()
    except:
        raise CMException('vnc_detach')
