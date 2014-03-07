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

"""@package src.cm.views.utils.vm_threads
@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <mn@mnabozny.pl>
"""
import threading
import libvirt
import time

#from cm.utils import message
from common.states import farm_states #,vm_states
from cm.models.vm import VM
from cm.utils import log
from django.db import transaction

#TODO:add global threads
#threads = {}



#class VMThread definition and its methods
class VMThread(threading.Thread):
    def __init__(self, vm, action, shared=None):
        threading.Thread.__init__(self)
        self.vm = vm
        self.action = action
        self.shared = shared
        
    def terminate(self):
        log.info(0, "Terminate vm %d" % (self.vm.id))
        return self._Thread__stop()

    def create(self):
        """
        Starts VM's thread.
        -# Gets VM's record from database (basing on vm_id) (if exists).
        -# Copies image chosen for this VM.
        -# Connects to Libvirt and generate template for it.
        -# Creates Libvirt domain.
        -# Sets VM's state as *running*
        -# If VM is element of farm, it sets proper farm state.
        """
        # TODO: Assign ip address from node ip addresses
        # try:
        #     vm = VM.objects.get(id=self.vm)
        #     #vm = Session.query(VM).get(self.vm_id)
        # except Exception, e:
        #     log.exception(0, 'Cannot find vm %d: %s'%(self.vm, e))
        #     return
        try:
            log.info(self.vm.user_id, "Copy image from %s to %s" % (self.vm.system_image.path, self.vm.path))
            self.vm.system_image.copy_to_node(self.vm)
        except Exception, e:
            log.exception(self.vm.user_id, 'Libvirt error for %d: %s' % (self.vm.id, e))
            self.vm.set_state('failed')
            #TODO: message
            #message.error(vm.user_id, 'vm_create', {'id': vm.id, 'name': vm.name})
            self.vm.node.lock()
            self.vm.save(update_fields=['state'])
            return
        
        #TODO: network part
        log.debug(self.vm.user_id, "Attaching network")
        try:
            for lease in self.vm.lease_set.all():
                lease.attach_node()
        except Exception, e:
            log.exception(self.vm.user_id, "Cannot create network")
            self.vm.set_state('failed')
            self.vm.save(update_fields=['state'])
            #message.error(vm.user_id, 'vm_create', {'id': vm.id, 'name': vm.name})
            self.vm.node.lock()
            self.vm.node.save()
            return

        log.info(self.vm.user_id, "Connecting libvirt and generating template")
        try:
            conn = libvirt.open(self.vm.node.conn_string)
            tmpl = self.vm.libvirt_template()
            log.debug(self.vm.user_id, "Create from template: %s" % tmpl)
        except Exception, e:
            log.exception(self.vm.user_id, "Cannot connect to libvirt")
            self.vm.set_state('failed')
            #TODO:
            #message.error(vm.user_id, 'vm_create', {'id': vm.id, 'name': vm.name})
            self.vm.node.lock()
            self.vm.save(update_fields=['state'])
            return
        
        log.info(self.vm.user_id, "Creating libvirt domain")
        try:
            domain = conn.createXML(tmpl, 0)
            self.vm.libvirt_id = domain.ID()
            self.vm.save()
            log.debug(self.vm.user_id, "New domain id: %d" % domain.ID())
        except Exception, e:
            log.exception(self.vm.user_id, 'Libvirt error: %s' % e)
            self.vm.set_state('failed')
            #TODO:message
            #message.error(vm.user_id, 'vm_create', {'id': vm.id, 'name': vm.name})
            self.vm.node.lock()
            self.vm.save()
            return
        
        try:
            self.vm.set_state('running')
            if self.vm.is_head():
                #TODO: farm.set_state
                self.vm.farm.state = farm_states['init_head']
                self.vm.farm.save()
            # elif self.vm.is_farm():
            #     self.shared['lock'].acquire()
            #     self.shared['counter'] = self.shared['counter'] - 1
            #     if self.shared['counter'] == 0:
            #         self.vm.farm.state = farm_states['nodes_copied']
            #         self.shared['lock'].release()
        except Exception, e:
            self.vm.set_state('failed')
            self.vm.node.lock()
            #TODO:
            #message.error(vm.user_id, 'vm_create', {'id': vm.id, 'name': vm.name})
            log.exception(self.vm.user_id, 'Domain not started: %s' % str(e))
            self.vm.save(update_fields=['state'])
            return
        
        try:
            self.vm.save(update_fields=['state'])
        except Exception, e:
            log.exception(self.vm.user_id, 'Cannot update database: %s' % str(e))
            return
        
    def delete(self):
        """
        Ends VM's thread.
        
        -# Unassigns public IP.
        -# Deletes VM.
        """
        try:
            VM.objects.update()
            vm = VM.objects.get(pk=self.vm.id)
            #vm = Session.query(VM).get(self.vm_id)
        except Exception, e:
            log.exception(0, 'Cannot find vm %d: %s'%(self.vm.id, e))
            return
        log.debug(vm.user_id, "VM Destroy")

        #TODO: Move to entites.vm release resources
        #for lease in vm.public_leases:
        #    lease.unassign()
        
        vm.delete()
        return

    def reset(self):
        """
        Restarts VM.
        
        -# Connects to Libvirt.
        -# Sets VM's state as *restart*.
        -# Restarts it.
        -# Sets VM's state back as *running*.
        """
        log.debug(self.vm.user_id, "VM Reboot")

        self.vm.set_state('restart')
        try:
            self.vm.save()
        except:
            log.exception(self.vm.user_id, 'Cannot set vm state')
            return
        
        try:
            domain = self.vm.lv_domain()
            domain.reset(0)
            self.vm.libvirt_id = domain.ID()
        except:
            self.vm.node.lock()
            #TODO:
            #message.error(vm.user_id, 'vm_restart', {'id': vm.id, 'name': vm.name})
            self.vm.set_state('failed')
            log.exception(self.vm.user_id, 'Cannot restart machine')
            
            try:
                self.vm.save()
            except:
                log.exception(self.vm.user_id, 'Cannot update libvirt ID')
                return
            
            return
            
        # Update state state
        self.vm.set_state('running')
        try:
            self.vm.save()
        except:
            log.exception(self.vm.user_id, 'Cannot set vm state')
            return

    def run(self):
        """
        Runs proper action depending on \ self.action.
        """
        #TODO: 
        #global threads
        #threads[self.vm_id] = self
        #time.sleep(5)
        with transaction.commit_manually():
            try:
                if self.action == 'create':
                    self.create()
                elif self.action == 'delete':
                    self.delete()
                elif self.action == 'reset':
                    self.reset()
                transaction.commit()
            except:
                log.exception(0, 'thread_exception')
                transaction.rollback()
        #TODO:
        #del threads[self.vm_id]