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
"""@package src.cm.models.command
"""

import json
import threading
from time import sleep

from django.db import models, transaction

from cm.models.vm import VM
from cm.utils import log
from cm.utils.exception import CMException
from cm.utils.threads.vm import VMThread
from common import response
from common.states import command_states, vm_states, farm_states
from cm.utils import message


class Command(models.Model):
    name = models.CharField(max_length=1000)
    args = models.CharField(max_length=100000)
    state = models.IntegerField()
    response = models.CharField(max_length=100000, null=True)
    vm = models.ForeignKey(VM)

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return "%s %s" % (self.name, self.args)

    def dict(self):
        """
        @returns{dict} command's data
        \n fields:
        @dictkey{id,int} id of this Command
        @dictkey{name,string} name of this Command
        @dictkey{args} args of the Command
        @dictkey{status} @seealso{src.common.states.available_network_states}
        @dictkey{response}
        """
        r = {}
        r['id'] = self.id
        r['name'] = self.name
        r['args'] = self.args
        r['state'] = self.state
        r['response'] = self.response
        return r

    @staticmethod
    def add_command(name, user_id, vm_id, **kwargs):
        """
        @parameter{name,string} Command to add for machine @prm{vm_id}
        @parameter{user_id,int}
        @parameter{vm_id,int}
        @parameter{kwargs,dict} key word args for the called function
        """
        cmd = Command()
        cmd.vm_id = vm_id
        cmd.name = name
        cmd.args = json.dumps(kwargs)
        cmd.state = command_states['pending']
        cmd.response = None
        log.debug(user_id, "Add command %s for machine %s" % (name, vm_id))
        cmd.save()
        return cmd

    @staticmethod
    def execute(name, user_id, vm_id, **kwargs):
        """
        Method executes command @prm{name} on the specified VM.
        User with id @prm{user_id} must be the owner of that VM.

        @parameter{name,string} name of the function to execute
        @parameter{user_id,long} id of the declared VM owner
        @parameter{vm_id,int} id of the VM on which command needs to be executed
        @parameter{kwargs,dict} keyword args for the called function

        @raises{ctx_timeout,CMException}
        @raises{ctx_execute_command,CMException}
        """
        vm = VM.get(user_id, vm_id)

        try:
            cmd = Command.add_command(name, user_id, vm_id, **kwargs)
            transaction.commit()
            log.debug(user_id, "Command state %s for machine %s" % (cmd.state, vm_id))

            dom = vm.lv_domain()
            dom.sendKey(0, 500, [113], 1, 0)

            retry = 3
            retry_factor = 1.2
            retry_time = 1
            try:
                while retry > 0:
                    log.debug(user_id, "Check if command %s is finished for machine %s" % (cmd.id, vm_id))
                    Command.objects.update()
                    cmd = Command.objects.get(id=cmd.id)
                    log.debug(user_id, "Checked command status: %s, %s, %s" % (cmd.state, command_states['finished'], bool(cmd.state == command_states['finished'])))
                    if cmd.state == command_states['finished']:
                        log.debug(user_id, "Response %s from machine %s" % (cmd.response, vm_id))
                        break
                    elif cmd.state == command_states['failed']:
                        raise CMException('ctx_' + name)
                    retry -= 1
                    retry_time *= retry_factor
                    sleep(retry_time)
            except:
                raise
            finally:
                cmd.delete()

            if retry == 0:
                log.debug(user_id, "Command %s for machine %s - TIMEOUT" % (name, vm_id))
                raise CMException('ctx_timeout')

            return cmd.response or ''
        except CMException:
            raise
        except Exception:
            log.exception(user_id, 'Execute command')
            raise CMException('ctx_execute_command')

    @staticmethod
    def hello(vm_ip, **args):
        """
        First function which must be called by VMs ctx module. It registers VM with status 'running ctx',
        also serves a special role when creating farms (tracking head, and worker nodes)

        @parameter{vm_ip,string}
        @parameter{args}
        """
        vm = VM.get_by_ip(vm_ip)
        log.debug(vm.user_id, "Hello from vm %d ip: %s" % (vm.id, vm_ip))

        vm.ctx_api_version = args.get('version', None)
        vm.state = vm_states['running ctx']

        if vm.ssh_username and vm.ssh_key:
            Command.execute('add_ssh_key', vm.user_id, vm.id, user=vm.ssh_username, ssh_key=vm.ssh_key)

        if vm.is_head():
            Command.register_head(vm)
        elif vm.is_farm():
            Command.register_node(vm)

        try:
            vm.save(update_fields=['state', 'ctx_api_version'])
        except Exception, e:
            log.error(vm.user_id, "Cannot update database for vm %d: %s" % (vm.id, e.message))
            return response('ctx_error', "Cannot update database: %s" % e.message)

        return 'ok'

    @staticmethod
    def name_to_farm(farm_name, vm_name):
        """
        Replaces farm name to "farm" word.

        @parameter{farm_name,string} farm name
        @parameter{vm_name,string} vm name
        """
        return vm_name.replace(farm_name, 'farm')

    @staticmethod
    def register_node(vm):
        """
        Called from CLM when registering worker nodes of the farm

        @parameter{vm,vm} VM database mapper
        """
        log.debug(vm.user_id, "machine %d: registered as worker node" % vm.id)

        try:
            hosts = vm.farm.hosts()
            log.debug(vm.user_id, "vm: %d, host list to inject into WNs: %s" % (vm.id, str(hosts)))

            Command.execute('add_ssh_key', vm.user_id, vm.id, user=vm.ssh_username, ssh_key=vm.ssh_key)
            Command.execute('update_hosts', vm.user_id, vm.id, hosts_list=hosts, user=vm.ssh_username)
            Command.execute('set_hostname', vm.user_id, vm.id, hostname=vm.name.replace(vm.farm.name, 'farm'))

        except Exception:
            log.exception(vm.user_id, 'configuring farm failed for machine %d' % vm.id)
            raise Exception('configuring farm failed')
        log.info(vm.user_id, 'WN %d registered' % vm.id)

    @staticmethod
    def register_head(vm):
        """
        Head registration process:
        - Creates ssh keys and sets their values for WN;
        - Inserts VMs into the database;
        - Then starts VMThreads which create actual machines.

        Called when registering farms head.

        @parameter{vm,VM} instance of the VM to be registered as head
        """
        log.debug(vm.user_id, "machine %d: registered as head" % vm.id)

        log.debug(vm.user_id, "creating lock for machine %d in farm %d" % (vm.id, vm.farm_id))
        # skip if farm is already configured - reboot head
        if vm.is_head() == True and vm.farm.state == farm_states['running']:
            return

        vms = []
        if vm.farm.state == farm_states['init_head']:
            vm.farm.state = farm_states['running']
            vm.farm.save()

            log.info(vm.user_id, 'generating ssh keys on head %d' % vm.id)

            try:
                r = Command.execute('generate_key', vm.user_id, vm.id)
                r = json.loads(r)
                log.info(vm.user_id, 'generated key: %s for machine %d' % (r, vm.id))
                for wn in vm.farm.vms.all():
                    wn.ssh_username = 'root'
                    wn.ssh_key = r
                    wn.save()
                    if not wn.is_head():
                        vms.append(wn)
                ssh_username = 'root'
                ssh_key = r
                log.debug(vm.user_id, 'appended %d vms to farm [id:%d]' % (vm.farm.vms.count() - 1, vm.id))  # excluding head

                Command.add_command('add_ssh_key', vm.user_id, vm.id, user=ssh_username, ssh_key=ssh_key)
                Command.add_command('update_hosts', vm.user_id, vm.id, hosts_list=vm.farm.hosts(), user=ssh_username)
                Command.execute('set_hostname', vm.user_id, vm.id, hostname=vm.name.replace(vm.farm.name, 'farm'))

            except Exception:
                log.exception(vm.user_id, '')
                vm.farm.state = farm_states['unconfigured']
                message.error(vm.id, 'farm_create', {'id': vm.farm.id, 'name': vm.farm.name})
        log.info(vm.user_id, 'Head %d registered' % vm.id)
        shared = {"counter": len(vms), "lock": threading.Lock()}
        for vm in vms:
            thread = VMThread(vm, 'create', shared)
            thread.start()
            log.debug(vm.user_id, 'vm thread created [vm id:%d]' % vm.id)
