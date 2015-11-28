# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
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
"""@package src.cm.models.vm
"""
from cm.settings import VNC_PORTS, NOVNC_PORTS

from cm.models.node import Node
from cm.models.public_ip import PublicIP
from cm.models.template import Template
from cm.models.user import User
from cm.models.farm import Farm
from cm.models.system_image import SystemImage
from cm.models.iso_image import IsoImage
from cm.models.lease import Lease
from cm.models.available_network import AvailableNetwork
from cm.utils.exception import CMException
from cm.utils import log
from cm.utils.monia import RrdHandler

from django.db import models, transaction
from django.conf import settings
from django.template import loader, Context
from django.conf import settings as django_settings

from common.states import vm_states, image_states, farm_states, lease_states, vnc_states
from common.utils import password_gen

from datetime import datetime
import os
import uuid
import libvirt
import subprocess

from netaddr import IPNetwork
from cm.utils import message


class VM(models.Model):
    """
    @model{vm} Virtual machine class

    Virtual Machines creation and management are the main features of the CC1
    system. They make use of the node's CPU (Node) to emulate physical
    hardware. They should be considered as remote workstations with operating
    system (VMImage) running on them.

    VM may be created and further saved to VMImage or destroyed irrevocably.

    VM may have plugged resources of several types, so that it's functionality
    and access to it are extended.
    """
    name = models.CharField(max_length=128)
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
    template = models.ForeignKey(Template)
    system_image = models.ForeignKey(SystemImage)
    iso_image = models.ForeignKey(IsoImage, null=True, blank=True)
    libvirt_id = models.IntegerField()
    state = models.IntegerField()
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField(null=True, blank=True)
    ctx_key = models.CharField(max_length=128, null=True, blank=True)
    ctx_api_version = models.CharField(max_length=10, null=True, blank=True)
    vnc_passwd = models.CharField(max_length=45)

    ssh_key = models.TextField(null=True, blank=True)
    ssh_username = models.CharField(max_length=45, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    save_vm = models.IntegerField()
    farm = models.ForeignKey(Farm, related_name='vms', null=True)
    hostname = models.CharField(max_length=256, null=True, blank=True)
    vnc_port = models.IntegerField()
    novnc_port = models.IntegerField(default=0)
    vnc_enabled = models.IntegerField(default=0)
    reservation_id = models.IntegerField(default=0)
    user_data = models.CharField(max_length=32768, null=True, blank=True)

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return self.name

    @property
    def dict(self):
        """
        @returns{dict} this VM's data
        \n fields:
        @dictkey{id,int}
        @dictkey{user_id,int}
        @dictkey{name,string}
        @dictkey{state,int} @seealso{src.common.states.vm_states}
        @dictkey{leases,list(dict)}
        @dictkey{image_name,string}
        @dictkey{template_name,string}
        @dictkey{platform,string}
        @dictkey{description,string}
        @dictkey{vnc_endpoint,int}
        @dictkey{vnc_enabled,bool}
        @dictkey{vnc_passwd,string}
        @dictkey{iso_images,list(dict)}
        @dictkey{storage_images,list(dict)}
        @dictkey{cpu_load,int}
        """
        d = {}
        d['vm_id'] = self.id
        d['user_id'] = self.user.id
        d['name'] = self.name
        d['state'] = self.state
        d['leases'] = [l.dict for l in self.lease_set.all()]
        d['image_name'] = self.system_image.name
        d['image_id'] = self.system_image.id
        d['template_name'] = self.template.name
        d['platform'] = 0
        d['description'] = self.description or ''
        d['vnc_endpoint'] = '%s:%d' % (settings.VNC_ADDRESS, self.vnc_port)
        d['novnc_endpoint'] = '%s:%d' % (settings.VNC_ADDRESS, self.novnc_port)
        d['vnc_enabled'] = self.vnc_enabled
        d['vnc_passwd'] = self.vnc_passwd or ''

        if self.iso_image:
            d['iso_images'] = [{'id': self.iso_image.id, 'name': self.iso_image.name}]
        else:
            d['iso_images'] = []
        d['storage_images'] = [{'storage_image_id': img.id, 'name': img.name} for img in self.storage_images]
        d['cpu_load'] = self.cpu_load

        return d

    @property
    def long_dict(self):
        """
        @returns{dict} this VM's extended data
        \n fields:
        @dictkey{id,int}
        @dictkey{user_id,int}
        @dictkey{name,string}
        @dictkey{state,int} @seealso{src.common.states.command_states}
        @dictkey{leases,list(dict)}
        @dictkey{image_name,string}
        @dictkey{template_name,string}
        @dictkey{platform,string}
        @dictkey{description,string}
        @dictkey{vnc_endpoint,int}
        @dictkey{vnc_enabled,bool}
        @dictkey{vnc_passwd,string}
        @dictkey{start_time,datetime.datetime}
        @dictkey{node,string} node's address
        @dictkey{libvirt_id,int}
        @dictkey{ssh_username,string}
        @dictkey{ssh_key,string}
        @dictkey{iso_images,list(dict)}
        @dictkey{storage_images,list(dict)}
        @dictkey{cpu_load,int}
        @dictkey{reservation_id,int}
        @dictkey{user_data,string}
        """
        d = {}
        d['vm_id'] = self.id
        d['user_id'] = self.user.id
        d['name'] = self.name
        d['state'] = self.state
        d['leases'] = [l.dict for l in self.lease_set.all()]
        d['image_name'] = self.system_image.name
        d['image_id'] = self.system_image.id
        d['template_name'] = self.template.name
        d['platform'] = 0
        d['description'] = self.description or ''
        d['vnc_endpoint'] = '%s:%d' % (settings.VNC_ADDRESS, self.vnc_port)
        d['novnc_endpoint'] = '%s:%d' % (settings.VNC_ADDRESS, self.novnc_port)
        d['vnc_enabled'] = self.vnc_enabled
        d['vnc_passwd'] = self.vnc_passwd or ''
        d['start_time'] = self.start_time
        delta = datetime.now() - self.start_time
        d['uptime'] = delta.seconds + 24 * 3600 * delta.days
        d['node'] = self.node.address
        d['libvirt_id'] = self.libvirt_id
        d['ssh_username'] = self.ssh_username or ''
        d['ssh_key'] = self.ssh_key or ''
        d['reservation_id'] = self.reservation_id
        d['user_data'] = self.user_data

        if self.iso_image:
            d['iso_images'] = [{'id': self.iso_image.id, 'name': self.iso_image.name}]
        else:
            d['iso_images'] = []
        d['storage_images'] = [{'storage_image_id': img.id, 'name': img.name, 'disk_controller': img.disk_controller}
                               for img in self.storage_images]
        d['cpu_load'] = self.cpu_load
        return d

    @staticmethod
    def create(user, name, description, image_id, template_id, public_ip_id, iso_list, disk_list, vnc, groups,
               ssh_key=None, ssh_username=None, count=1,
               farm=None, head_template_id=None, node_id=False, lease_id=None, user_data=None):
        from cm.models.storage_image import StorageImage
        from cm.utils.threads.vm import VMThread

        template = Template.get(template_id)
        image = SystemImage.get(user.id, image_id, groups)

        if image.state != image_states['ok']:
            raise CMException('image_unavailable')

        if farm:
            head_template = Template.get(head_template_id)
            wn_template = template
            user.check_quota([(head_template, 1), (wn_template, count)])
            count += 1
        else:
            user.check_quota([(template, count)])

        vms = []

        reservation_id = None

        for i in range(count):
            # create VM instance
            log.debug(user.id, "Looking for node")
            node = Node.get_free_node(head_template, image, node_id) if farm and i == 0 else Node.get_free_node(template, image, node_id)
            log.info(user.id, 'Selected node: %d' % node.id)
            vm = VM()
            vm.libvirt_id = -1
            if farm:
                if i == 0:
                    vm.name = '%s-head' % name
                    vm.description = 'Farm head'
                    vm.template = head_template
                else:
                    vm.name = '%s-wn%d' % (name, i)
                    vm.description = 'Worker Node'
                    vm.template = wn_template
            else:
                vm.template = template
                vm.description = description
                if count > 1:
                    vm.name = '%s_%d' % (name, i + 1)
                else:
                    vm.name = name
            vm.user = user
            vm.state = vm_states['init']
            vm.start_time = datetime.now()
            vm.system_image = image
            vm.node = node
            vm.save_vm = True
            if farm:
                vm.farm = farm

            # Find first free vnc port
            used_ports = VM.objects.exclude(state__in=[vm_states['closed'], vm_states['erased']]).values_list('vnc_port', flat=True)

            for new_vnc_port in xrange(VNC_PORTS['START'], VNC_PORTS['END'] + 1):
                if new_vnc_port not in used_ports and new_vnc_port not in VNC_PORTS['EXCLUDE']:
                    break
            else:
                raise CMException('vm_vnc_not_found')

            log.debug(user.id, "Found vnc port: %d" % new_vnc_port)
            vm.vnc_port = new_vnc_port

            # Find first free novnc port
            used_ports = VM.objects.exclude(state__in=[vm_states['closed'], vm_states['erased']]).values_list('novnc_port', flat=True)
            for new_novnc_port in xrange(NOVNC_PORTS['START'], NOVNC_PORTS['END'] + 1):
                if new_novnc_port not in used_ports and new_novnc_port not in NOVNC_PORTS['EXCLUDE']:
                    break
            else:
                raise CMException('vm_novnc_not_found')

            log.debug(user.id, "Found novnc port: %d" % new_novnc_port)
            vm.novnc_port = new_novnc_port

            if vnc:
                vm.attach_vnc()
            vm.vnc_passwd = password_gen(13, chars=['letters', 'digits'], extra_chars='!@#$%^&*()')
            vm.ssh_key = ssh_key
            vm.ssh_username = ssh_username
            vm.user_data = user_data
            vm.save()

            if not reservation_id:
                reservation_id = vm.id

            vm.reservation_id = reservation_id
            vm.save()

            if farm and i == 0:
                farm.head = vm
            vms.append(vm)

            log.debug(user.id, "Attaching disks")
            disk_devs = []
            if i == 0 and disk_list:
                for disk_id in disk_list:
                    log.debug(user.id, 'Attaching disks to first VM')
                    disk = StorageImage.get(user.id, disk_id)
                    if disk.vm != None:
                        raise CMException('image_attached')
                    while disk.disk_dev in disk_devs:
                        disk.disk_dev += 1
                    disk_devs.append(disk.disk_dev)
                    disk.vm = vm
                    disk.save()

            log.debug(user.id, "Attaching CD")
            if i == 0 and iso_list:
                for iso_id in iso_list:
                    log.debug(user.id, 'Attaching iso to first VM')
                    # cd image have not be attached to any other vm
                    iso = IsoImage.get(user.id, iso_id)
                    iso.check_attached()
                    vm.iso_image = iso
                    vm.save()

        for i, vm in enumerate(vms):
            if lease_id != None:
                lease = Lease.objects.get(id=lease_id)

                if lease.user_network.user != user:
                    raise CMException('lease_permission')

                if lease.vm != None:
                    raise CMException('lease_attached')
                lease.vm = vm
                log.debug(user.id, "Attached ip: %s" % lease.address)
            else:
                lease = AvailableNetwork.get_lease(user)
                lease.vm = vm
                lease.save()
                log.debug(user.id, "Attached ip: %s" % lease.address)

            if i == 0 and public_ip_id > 0:
                log.debug(user.id, "Attaching PublicIP")
                try:
                    publicip = PublicIP.objects.filter(user=user).get(id=public_ip_id)
                    publicip.assign(lease)
                    publicip.save()
                except Exception, e:
                    log.exception(user.id, str(e))
                    raise CMException("lease_not_found")

        return vms

    # make connection to the node of the VM, refresh the storagePool 'Images',
    # then get the path of StorageVol 'info' and initialize the path attribute
    # with the correct path making join with os path
    @property
    def path(self):
        """
        @returns{string} path to this VM on the Storage
        """
        conn = libvirt.open(self.node.conn_string)
        storage = conn.storagePoolLookupByName('images')
        storage.refresh(0)
        path = storage.storageVolLookupByName('info').path()
        conn.close()
        return os.path.join(os.path.dirname(path), str(self.id))

    def is_head(self):
        return bool(self.farm) and self == self.farm.head

    def is_farm(self):
        return bool(self.farm)

    # create a django template and render it with VM context
    def libvirt_template(self):
        """
        @returns{string} Libvirt XML template
        """
        try:
            lv_template = loader.get_template("%s.xml" % self.node.driver)
            c = Context({'vm': self,
                         'uuid': uuid.uuid1(),
                         'memory': self.template.memory * 1024,
                         'cpu': self.template.cpu,
                         'image_path': self.path
            })
            # and render it
            domain_template = lv_template.render(c)
        except Exception, e:
            log.debug(self.user.id, str(e))
        return domain_template

    # create a django template for network
    def network_template(self):
        """
        @returns{string} Libvirt network XML template
        """
        # Try to configure django
        try:
            django_settings.configure()
        except:
            pass
        try:
            # Open template file
            template = open("%s/%s-network.xml" % (settings.TEMPLATE_DIR, settings.NETWORK_TYPE)).read()

            # Create django template
            lv_template = loader.get_template_from_string(template)
            c = Context({'vm': self})
            lv_template = lv_template.render(c)
        except Exception, e:
            log.debug(self.user.id, str(e))
        return lv_template

    @staticmethod
    def get(user_id, vm_id):
        """
        @parameter{user_id,int} declared owner of the VM
        @parameter{vm_id,int} id of the requested VM

        @returns{VM} requested VM instance, if it belongs to declared owner

        @raises{vm_get,CMException} no such VM
        @raises{user_permission,CMException} requested VM doesn't belong to
        declared User.
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except:
            raise CMException('vm_get')

        if vm.user.id != user_id:
            raise CMException('user_permission')

        return vm

    @staticmethod
    def admin_get(vm_id):
        """
        @parameter{vm_id,int} id of the requested VM

        @returns{VM} requested VM instance

        @raises{vm_get,CMException} no such VM
        """

        try:
            vm = VM.objects.get(pk=vm_id)
        except:
            raise CMException('vm_get')

        return vm

    def save_image(self):
        """
        Method saves VM to image with VM's name, description and parameters.
        """
        self.set_state('saving')
        try:
            self.save(update_fields=['state'])
            transaction.commit()
        except Exception, e:
            log.exception(self.user.id, 'save img')
            return

        img = SystemImage.create(name=(self.name + "_autosave" if self.save_vm == 1 else self.name),
                                 description=self.description, user=self.user, platform=self.system_image.platform,
                                 disk_controller=self.system_image.disk_controller,
                                 network_device=self.system_image.network_device,
                                 video_device=self.system_image.video_device)
        img.size = self.system_image.size
        img.save()

        try:
            img.copy_to_storage(self, img)
        except Exception, e:
            self.set_state('saving failed')
            self.node.lock()
            message.error(self.user.id, 'vm_save', {'id': self.id, 'name': self.name})
            try:
                img.delete()
                transaction.commit()
            except Exception, e:
                log.exception(self.user.id, "Cannot commit changes: %s" % e)
            log.exception(self.user.id, "Cannot move image - error code: %s" % e)
            return

        img.state = image_states['ok']
        try:
            img.save()
        except Exception, e:
            log.error(self.user.id, "Cannot commit changes: %s" % e)
            message.error(self.user.id, 'vm_save', {'id': self.id, 'name': self.name})

        if self.is_head():
            message.info(self.user_id, 'farm_saved', {'farm_name': self.farm.name})
        else:
            message.info(self.user_id, 'vm_saved', {'vm_name': self.name})

    def remove(self):
        """
        """
        if not self.state in (vm_states['closing'], vm_states['saving']):
            self.set_state('closing')
            try:
                self.save(update_fields=['state'])
            except Exception, e:
                log.exception(self.user.id, 'closing img')
                return

        # Remove image
        try:
            conn = libvirt.open(self.node.conn_string)
            pool = conn.storagePoolLookupByName('images')
            pool.refresh(0)
            vol = pool.storageVolLookupByName(str(self.id))
            vol.delete(0)
            conn.close()
        except Exception, e:
            log.debug(self.user.id, "Cannot remove image: %s" % str(e))

            self.node.lock()
            self.set_state('failed')

            message.error(self.user.id, 'vm_destroy', {'id': self.id, 'name': self.name})
            try:
                self.save()
            except Exception, e:
                log.exception(self.user.id, "Cannot commit changes: %s" % e)
            return

    # TODO:
    # releases node's resources: vnc, public lease, network lease
    def release_resources(self):
        """
        Method releases node's resources.
        """
        log.debug(self.user.id, "Detaching vnc for vm %d" % self.id)
        if self.vnc_enabled == vnc_states['attached']:
            try:
                self.detach_vnc()
            except Exception, e:
                log.debug(self.user.id, str(e))
                self.set_state('failed')
                self.node.lock()

        log.debug(self.user.id, "Detaching leases for vm %d" % self.id)
        for lease in self.lease_set.all():
            log.debug(self.user.id, "\t...detaching lease %s" % lease.address)
            lease.detach_node()

        # detach volume disks
        # TODO:test
        log.debug(self.user.id, "Detaching disks for vm %d" % self.id)
        for img in self.storage_images:
            img.vm = None
            img.save()

        # detach cd image
        self.iso_image = None

        try:
            self.save(update_fields=['vnc_enabled'])
        except Exception, e:
            log.exception(self.user_id, "Cannot update resurce information: %s", str(e))
            self.node.lock()
            return

    def lv_destroy(self):
        """
        Method destroyes VM by libvirt.
        """
        domain = self.lv_domain()
        domain.destroy()

    # delete VM AND release resources
    def delete(self):
        """
        Method releases resources taken by deleted ex VM.
        """

        VM.objects.update()
        self = VM.objects.get(pk=self.id)
        if self.save_vm > 0:
            log.debug(self.user.id, 'Saving image')
            self.save_image()
        log.debug(self.user.id, 'Removing image')
        self.remove()

        log.debug(self.user.id, 'Releasing resources')
        self.release_resources()

        # Update vm state
        self.set_state('closed')
        """
        #TODO:
         if self.is_head():
            self.farm.state = farm_states['closed']
        """
        self.stop_time = datetime.now()
        try:
            self.save(update_fields=['state', 'stop_time'])
        except Exception, e:
            log.exception(self.user.id, "Cannot commit changes: %s" % e)

    def lv_domain(self):
        """
        Connects to Libvirt and returns its domain.

        @returns Libvirt domain

        @raises{vm_get_lv_domain,CMException}
        """
        try:
            conn = libvirt.open(self.node.conn_string)
            domain = conn.lookupByID(self.libvirt_id)
            # TODO: could we close connection here?
            # conn.close()
        except Exception, e:
            self.node.lock()
            self.set_state('failed')
            if self.is_farm() and self.is_head():
                self.farm.state = farm_states['failed']
            self.save()
            log.exception(self.user.id, str(e))
            raise CMException('vm_get_lv_domain')
        return domain


    @property
    def storage_images(self):
        """
        @returns{StorageImage} vm's storage images

        @raises{storage_image_attach,CMException}
        """
        return self.storageimage_set.all()

    @property
    def iso_images(self):
        """
        @returns{CDImage} vm's iso images

        @raises{iso_image_attach,CMException}
        """
        # TODO: cd Image can be only one for each VM. sure?
        """
        letter = ord('a')
        for img in images:
            img.disk_dev = 'sr%s' % chr(letter)
            letter += 1
        """
        image = self.iso_image
        image.disk_dev = 1

        try:
            image.save()
        except Exception:
            raise CMException('iso_image_attach')
        return image

    def set_state(self, state):
        """
        @parameter{state,string} new state for entity, value in 'turned off',
        'restart', 'running', 'running ctx', 'turned off', 'saving',
        'closing', 'init', 'closed', 'saving failed',  'failed', 'suspend',
        'ereased'

        @raises{vm_wrong_state,CMException}
        """

        # Key - destination state
        # Values - actual available states
        states = {'init': (),
                  'running': ('init', 'turned off', 'restart',),
                  'running ctx': ('running', 'running ctx',),
                  'closing': ('turned off', 'running', 'running ctx', 'saving', 'turned off',),
                  'closed': ('saving', 'closing', 'erased'),
                  'saving': ('running', 'running ctx',),
                  'saving failed': ('saving',),
                  'failed': ('init', 'running', 'running ctx', 'closing', 'closed', 'saving', 'saving failed', 'failed',
                             'turned off', 'suspend', 'restart', 'erased'),
                  'turned off': ('running', 'init',),
                  'suspend': ('running', 'running ctx',),
                  'restart': ('running', 'running ctx',),
                  'erasing': (
                  'init', 'running', 'running ctx', 'closing', 'closed', 'saving', 'saving failed', 'failed',
                  'turned off', 'suspend', 'restart', 'erased', 'erasing'),
                  'erased': ('erasing', 'erased')
        }

        # Find my state:
        my_state = False
        for s in vm_states.keys():
            if self.state == vm_states[s]:
                my_state = s

        log.info(self.user.id, "Changing state from %s to %s for %d" % (my_state, state, self.id))

        # Check if VM could go from actual state to given
        if (my_state not in states[state] or my_state == False) and my_state != 'erasing':
            raise CMException('vm_wrong_state', '%s -> %s for %d' % (my_state, state, self.id))

        self.state = vm_states[state]
        self.save(update_fields=['state'])

        # Lock node on fail
        if state in ('failed', 'saving failed') and my_state != 'erasing':
            self.node.lock()

    @staticmethod
    def erase(vm):
        """
        Remove all after-effects of the failed vm and free the resources.
        """
        vm.save_vm = 0
        vm.set_state('erasing')
        try:
            vm.save()
            transaction.commit()
        except:
            log.error(vm.user.id, 'Cannot set save=0')

        conn = libvirt.open(vm.node.conn_string)
        try:
            domain = conn.lookupByID(vm.libvirt_id)
            domain.destroy()
        except Exception, e:
            log.error(vm.user.id, "Cannot find libvirt domain (by ID): %d (%s)" % (vm.libvirt_id, str(e)))
            try:
                domain = conn.lookupByName("vm-%d-%d" % (vm.id, vm.user.id))
                domain.destroy()
            except Exception, e:
                log.error(vm.user.id, "Cannot find libvirt domain (by name): %d (%s)" % (vm.libvirt_id, str(e)))

        try:
            pool = conn.storagePoolLookupByName('images')
            pool.refresh(0)
            vol = pool.storageVolLookupByName(str(vm.id))
            vol.delete(0)
        except:
            log.error(vm.user.id, "Cannot remove vm image (or other SSH error)")

        try:
            vm.release_resources()
        except Exception, e:
            log.error(vm.user.id, "Cannot release resources: %s" % str(e))

        for l in vm.lease_set.all():
            try:
                l.detach_node()
            except Exception, e:
                log.error(vm.user.id, "Cannot detach lease: %s" % str(e))

            l.state = lease_states['free']
        vm.state = vm_states['erased']
        vm.stop_time = datetime.now()

        try:
            vm.save()
        except:
            log.error(vm.user.id, "Cannot commit changes.")
        conn.close()

    @property
    def cpu_load(self):
        res = ['60', '300', '900']
        try:
            return RrdHandler().cpu_load('vm-%d-%d' % (self.id, self.user_id), res)
        except CMException, e:
            log.error(self.user_id, 'cpu_load: %s' % str(e))
            return dict([(x, '') for x in res])

    @staticmethod
    def destroy(vms):
        """
        @parameter{vms}
        @response result
        """
        results = []
        for vm in vms:
            vm = VM.objects.get(pk=vm.id)
            log.debug(vm.user.id, "Killing VM id: %s, state: %s" % (vm.id, vm.state))
            # Check for VM state
            if vm.state in (vm_states['closing'], vm_states['saving']):
                results.append({'status': 'vm_already_closing', 'data': ''})
                continue

            if vm.state in (vm_states['erased'], vm_states['closed']):
                results.append({'status': 'vm_wrong_state', 'data': ''})
                continue

            vm.save_vm = 0

            try:
                vm.save()
                transaction.commit()
                vm.lv_destroy()
            except Exception, e:
                log.exception(vm.user.id, 'error destroying VM: %s' % str(e))
                results.append({'status': 'vm_destroy', 'data': ''})
                message.error(vm.user_id, 'vm_destroy', {'id': vm.id, 'name': vm.name})
                continue

            results.append({'status': 'ok', 'data': ''})

        return results

    @staticmethod
    def get_by_ip(ip):
        ip = str(IPNetwork('%s/30' % ip).network)
        try:
            vm = VM.objects.filter(lease__address=ip)[0]
        except:
            raise CMException('vm_get')

        return vm

    @staticmethod
    def reset(vms):
        from cm.utils.threads.vm import VMThread

        results = []
        for vm in vms:
            if vm.state in (vm_states['running'], vm_states['running ctx']):
                thread = VMThread(vm, 'reset')
                thread.start()
                results.append({'status': 'ok', 'data': ''})
            else:
                results.append({'status': 'vm_wrong_state', 'data': ''})

        return results

    def attach_vnc(self, reattach=False):
        if not self.state in (vm_states['init'], vm_states['running'], vm_states['running ctx']):
            raise CMException('vm_wrong_state')

        if self.vnc_enabled == vnc_states['attached'] and reattach == False:
            raise CMException('vm_vnc_attached')

        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-A", "CC1_VNC_REDIRECT", "-d", settings.VNC_ADDRESS, "-p", "tcp",
             "--dport", str(self.vnc_port), "-j", "DNAT", "--to-destination",
             "%s:%s" % (self.node.address, str(self.vnc_port))])
        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-A", "CC1_VNC_MASQUERADE", "-d", self.node.address, "-p", "tcp",
             "--dport", str(self.vnc_port), "-j", "MASQUERADE"])
        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-A", "CC1_VNC_REDIRECT", "-d", settings.VNC_ADDRESS, "-p", "tcp",
             "--dport", str(self.novnc_port), "-j", "DNAT", "--to-destination",
             "%s:%s" % (self.node.address, str(self.novnc_port))])
        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-A", "CC1_VNC_MASQUERADE", "-d", self.node.address, "-p", "tcp",
             "--dport", str(self.novnc_port), "-j", "MASQUERADE"])

        self.vnc_enabled = vnc_states['attached']

    def detach_vnc(self):
        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-D", "CC1_VNC_REDIRECT", "-d", settings.VNC_ADDRESS, "-p", "tcp",
             "--dport", str(self.vnc_port), "-j", "DNAT", "--to-destination",
             "%s:%s" % (self.node.address, str(self.vnc_port))])
        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-D", "CC1_VNC_MASQUERADE", "-d", self.node.address, "-p", "tcp",
             "--dport", str(self.vnc_port), "-j", "MASQUERADE"])

        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-D", "CC1_VNC_REDIRECT", "-d", settings.VNC_ADDRESS, "-p", "tcp",
             "--dport", str(self.novnc_port), "-j", "DNAT", "--to-destination",
             "%s:%s" % (self.node.address, str(self.novnc_port))])
        subprocess.call(
            ["sudo", "/sbin/iptables", "-t", "nat", "-D", "CC1_VNC_MASQUERADE", "-d", self.node.address, "-p", "tcp",
             "--dport", str(self.novnc_port), "-j", "MASQUERADE"])

        self.vnc_enabled = vnc_states['detached']

    @staticmethod
    def save_and_shutdown(user_id, vm, name, description):
        vm.description = description
        vm.name = name
        vm.save_vm = 2
        try:
            vm.save()
        except:
            raise CMException('vm_save')

        if vm.state != vm_states['running ctx']:
            raise CMException('vm_cannot_shutdown')

        try:
            from cm.models.command import Command

            Command.execute('shutdown', user_id, vm.id)
        except:
            raise CMException('vm_ctx_connect')
