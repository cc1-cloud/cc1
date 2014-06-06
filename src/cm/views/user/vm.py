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

"""@package src.cm.views.user.vm
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <di.dijo@gmail.com>
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
"""

from common.states import vm_states
from cm.utils.decorators import user_log
from cm.utils.exception import CMException
from cm.models.user import User
from cm.models.vm import VM
from cm.utils.threads.vm import VMThread
from cm.utils import message


@user_log(log=True)
def create(caller_id, name, description, image_id, template_id, public_ip_id, iso_list, disk_list, vnc, groups, count=1, user_data=None,
           ssh_key=None, ssh_username=None):
    """
    Creates virtual machines.
    @cmview_user

    @parameter{name,string}
    @parameter{description,string}
    @parameter{image_id,int}
    @parameter{template_id,int}
    @parameter{ip_id,int}
    @parameter{iso_list,list(int)} ISOs' ids
    @parameter{vnc}
    @parameter{groups}
    @parameter{user_data} data accessible via ec2ctx
    @parameter{ssh_key}
    @parameter{ssh_username}

    @returns @asreturned{src.cm.views.utils.vm.create()}
    """
    user = User.get(caller_id)
    try:
        user.check_points()
    except:
        message.warn(caller_id, 'point_limit', {'used_points': user.used_points, 'point_limit': user.points})
    vms = VM.create(user, name=name, description=description, image_id=image_id,
                    template_id=template_id, public_ip_id=public_ip_id, iso_list=iso_list, disk_list=disk_list,
                    vnc=vnc, groups=groups, count=count, user_data=user_data, ssh_key=ssh_key, ssh_username=ssh_username)

    for vm in vms:
        thread = VMThread(vm, 'create')
        thread.start()

    return [vm.dict for vm in vms]


@user_log(log=True)
def destroy(caller_id, vm_ids):
    """
    This function only destroys virtual machine. All cleanup (removing disk,
    saving, rescuing resources, ...) is done by hook through
    \c contextualization.update_vm method (yeah, intuitive).

    Simple sequence diagram:

    @code

            CLM        CM         CTX           Node (HOOK)
             .
            Destroy -->destroy
             |          |       (LV.destroy)
             |          |------------------------->HookScript
             .          .                          |
             .          .          ctx.update_vm<--|
             .          .           |              |
             .          .           |------------->cp
             .          .           |------------->rm
             .          .          update_resources

    @endcode

    @cmview_user

    @parameter{vm_ids,list} list of virtual machines' ids

    @response{src.cm.views.utils.image.destroy()}
    """
    vms = []
    for vm_id in vm_ids:
        vms.append(VM.get(caller_id, vm_id))
    return VM.destroy(vms)


@user_log(log=True)
def save_and_shutdown(caller_id, vm_id, name, description):
    """
    Calls src.cm.views.utils.image.save_and_shutdown() for the VM selected.

    @cmview_user

    @parameter{vm_id,int} id of the VM to save and shutdown.
    @parameter{name,string}
    @parameter{description,string}
    """
    user = User.get(caller_id)
    vm = VM.get(caller_id, vm_id)

    if user.used_storage + vm.system_image.size > user.storage:
        raise CMException('user_storage_limit')

    VM.save_and_shutdown(caller_id, vm, name, description)


@user_log(log=False, pack=False)
def get_list(caller_id):
    """
    Returns caller's VMs.
    @cmview_user

    @response{list(dict)} infos about caller's VMs
    """

    vms = VM.objects.exclude(state__in=[vm_states['closed'], vm_states['erased']]).filter(user__id__exact=caller_id)\
        .filter(farm=None).order_by('-id')
    vms_mod = [vm.dict for vm in vms]
    return vms_mod


@user_log(log=False)
def get_by_id(caller_id, vm_id):
    """
    Returns requested caller's VM.
    @cmview_user

    @parameter{vm_id,int} id of the requested VM

    @response{dict} VM's extended info
    """
    vm = VM.get(caller_id, vm_id)
    vm_mod = vm.long_dict
    return vm_mod


@user_log(log=True)
def reset(caller_id, vm_ids):
    """
    Restarts safely selected callers VMs
    @cmview_user

    @parameter{ids,list(int)} ids of the VMs to restart

    @response{src.cm.views.utils.image.restart()}
    """

    # get to check permissions on vms
    vms = []
    for vm_id in vm_ids:
        vms.append(VM.get(caller_id, vm_id))

    return VM.reset(vms)


@user_log(log=True)
def edit(caller_id, vm_id, name, description):
    """
    Changes selected VMs' parameters.
    Current should be get by src.cm.views.user.vm.get_by_id().
    @cmview_user

    @parameter{vm_id,int} id of the VM to edit
    @parameter{name,string}
    @parameter{description,string}

    @response{src.cm.views.utils.image.edit()}
    """
    vm = VM.get(caller_id, vm_id)

    vm.name = name
    vm.description = description
    vm.save(update_fields=['name', 'description'])


@user_log(log=True)
def attach_vnc(caller_id, vm_id):
    """
    Attaches VNC redirection to VM.
    @cmview_user

    @parameter{vm_id,int} id of the VM to have attached VM redirection

    @response{None}
    """
    vm = VM.get(caller_id, vm_id)
    vm.attach_vnc()

    try:
        vm.save()
    except:
        raise CMException('vnc_attach')


@user_log(log=True)
def detach_vnc(caller_id, vm_id):
    """
    Detaches VNC redirection from VM.
    @cmview_user

    @parameter{vm_id,int} id of the VM to have detached VM redirection
    @response{None}
    """
    vm = VM.get(caller_id, vm_id)
    vm.detach_vnc()

    try:
        vm.save()
    except:
        raise CMException('vnc_detach')
