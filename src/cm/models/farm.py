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

"""@package src.cm.models.farm
"""

from datetime import datetime

from django.db import models

from cm.models.user import User
from cm.utils import log
from cm.utils.exception import CMException
from common.states import farm_states, vm_states


class Farm(models.Model):

    user = models.ForeignKey(User)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    state = models.IntegerField()
    head = models.ForeignKey('VM', related_name='+')

    class Meta:
        app_label = "cm"

    def __unicode__(self):
        return self.name

    @property
    def dict(self):
        d = {}
        d["farm_id"] = self.id
        d["user_id"] = self.user.id
        d["name"] = self.name
        vms = list(self.vms.order_by('id'))
        d["vms"] = [vm.dict for vm in vms]
        d["state"] = self.state
        d["start_time"] = vms[0].start_time
        delta = datetime.now() - vms[0].start_time
        d['uptime'] = delta.seconds + 24 * 3600 * delta.days
        d["image_name"] = vms[0].system_image.name
        d["head_template_name"] = vms[0].template.name if len(vms) > 0 else ''
        d["template_name"] = vms[1].template.name if len(vms) > 1 else ''
        d["cpu"] = sum([vm.template.cpu for vm in vms])
        d["memory"] = sum([vm.template.memory for vm in vms])
        return d

    @staticmethod
    def get(user_id, farm_id):
        try:
            farm = Farm.objects.get(pk=farm_id)
        except:
            raise CMException('vm_get')

        if farm.user.id != user_id:
            raise CMException('user_permission')

        return farm

    @staticmethod
    def admin_get(farm_id):
        try:
            farm = Farm.objects.get(pk=farm_id)
        except:
            raise CMException('vm_get')

        return farm

    @staticmethod
    def create(user, name, description):
        farm = Farm()
        farm.name = name
        farm.user = user
        farm.description = description
        farm.state = farm_states['init']
        return farm

    @staticmethod
    def destroy(farms):
        """
        Destroyes farms' VMs (Head and Worker Nodes of each farm) without saving them.

        @parameter{farms,list} list of farms to destroy

        @response{list(dict)} list of statuses returned by destroyed VMs

        @raises{farm_wrong_state,CMException}
        @raises{farm_destroy,CMException}
        """
        from cm.models.vm import VM

        vm_resp = []
        for farm in farms:
            # those are states in which farm can not be destroyed
            if farm.state in (farm_states['init'], farm_states['closing'], farm_states['closed']):
                raise CMException('farm_wrong_state')

        for farm in farms:
            # stop all threads
            if farm.state == farm_states['init_head']:
                for vm in farm.vms.all():
                    if vm.is_head():
                        continue
                    vm.release_resources()
                    vm.state = vm_states['closed']
                    vm.stop_time = datetime.now()
                    vm.save()
                    log.debug(vm.user.id, "vm state %s" % vm.state)
                r = VM.destroy([farm.head])
            else:
                log.debug(farm.user_id, "killing wn: %s" % farm.vms)
                r = VM.destroy(farm.vms.all())

            if True in [x['status'] != 'ok' for x in r]:
                farm.state = farm_states['failed']
                try:
                    farm.save()
                except Exception:
                    raise CMException('farm_destroy')
            vm_resp.append(r)

            farm.state = farm_states['closed']

            try:
                farm.save()
            except Exception:
                raise CMException('farm_destroy')

            log.debug(farm.user_id, "session commited")
            for vm in farm.vms.all():
                log.debug(vm.user.id, "vm state %s" % vm.state)

        return vm_resp

    @staticmethod
    def save_and_shutdown(farm, name, description):
        """
        """
        from cm.models.vm import VM

        if farm.state == farm_states['failed']:
            raise CMException('farm_wrong_state')

        head_vm = farm.head
        try:
            head_vm.name = name
            head_vm.description = description
            head_vm.save_vm = 2
            head_vm.save()
            head_vm.save_image()
            head_vm.release_resources()
            head_vm.remove()
            head_vm.state = vm_states['closed']
            head_vm.save()
        except Exception:
            CMException('farm_save')

        node_vms = []
        if farm.state == farm_states['init_head']:
            for vm in farm.vms.all():
                if vm.is_head():
                    continue
                vm.release_resources()
                vm.state = vm_states['closed']
        else:
            for vm in farm.vms.all():
                node_vms.append(vm)
            VM.destroy(node_vms)

        try:
            farm.state = farm_states['closed']
            farm.save()
        except:
            CMException('farm_save')

    def hosts(self):
        hosts_list = []
        host_id = 1
        for vm in self.vms.all():
            if vm.is_head():
                # TODO: Change leases[0]
                hosts_list.append({"ip": vm.lease_set.all()[0].vm_address, "host_name": "farm-head"})
            else:
                hosts_list.append({"ip": vm.lease_set.all()[0].vm_address, "host_name": "farm-wn%d" % host_id})
                host_id += 1
        return hosts_list
