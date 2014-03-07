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
"""@package src.cm.models.disk_volume
"""

import os

from django.db import models

from cm.models.image import Image
from cm.models.vm import VM
from cm.utils import log
from cm.utils.exception import CMException


# from common.states import image_states, storage_states
# from common.hardware import disk_controllers
class StorageImage(Image):
    """
    @model{DISK_VOLUME}

    Storage type image's class.

    Disk Volume is one of the Images type. StorageImage class extends
    src.cm.models.image.Image class.

    Storage images are meant to collect data produced by VM it's attached to.
    It should be considered as storage disk. Data may be saved on it.

    There are several disk controllers to choose from. Only storage image
    with USB disk controller may be plugged to and unplugged from running
    VM on the fly. Other ones ought to be plugged while starting VM and are
    automatically unplugged when VM is closed or destroyed.
    """
    vm = models.ForeignKey(VM, null=True, blank=True)

    @classmethod
    def create(cls, name, description, user, disk_controller, size=0):
        image = Image.create(cls, name=name, description=description, user=user, size=size, progress=0, disk_dev=1, disk_controller=disk_controller)

        return image

    @property
    def dict(self):
        """
        @returns{dict} image's data
        \n fields:
        @dictkey{id}
        @dictkey{user_id,int}
        @dictkey{name}
        @dictkey{platform}
        @dictkey{description}
        @dictkey{creation_date}
        """
        d = self.dictImg()

        d['storage_image_id'] = self.id

        # fields for disk volume:

        if self.disk_dev is not None:
            d['disk_dev'] = 'sd%s' % chr(self.disk_dev + 98)
        else:
            d['disk_dev'] = ''

        # the vm id and name to which the disk volume is attached (or empty if no vm uses it)
        d['vm_id'] = self.vm.id if self.vm else ''
        d['vm_name'] = self.vm.name if self.vm else ''

        return d

    @staticmethod
    def get(user_id, disk_image_id):
        """
        @parameter{user_id,int} declared owner of the requested StorageImage
        @parameter{disk_image_id,int} id of the requested StorageImage

        @returns{StorageImage} requested StorageImage instance, provided it actually
        belongs to user_id.

        @raises{image_get,CMException} no such Image
        """

        try:
            image = StorageImage.objects.get(pk=disk_image_id)
        except:
            raise CMException('image_get')

        image.has_access(user_id)

        # check on state and storage?
        # if image.state != image_states['ok'] and image.storage.state != storage_states['ok']:
        #    raise CMException('image_unavailable')

        return image

    # returns True, if user_id is the owner of the storage image
    # (disk volumes are private). Otherwise exception is thrown.
    def has_access(self, user_id):
        """
        @parameter{user_id,int}

        @returns{bool}
        True, if user \c user_id is the owner of the image.
        Otherwise exception is thrown.

        @raises{image_permission,CMException}
        """
        if self.user.id != user_id:
            raise CMException('image_permission')
        return True

    # @returns VMImage instance for admin user
    @staticmethod
    def admin_get(disk_image_id):
        """
        Getter, which should be called by admin. It doesn't check Image's ownership.

        @parameter{img_id,int} id of the requested Image

        @returns{Image} instance of the requested Image
        @raises{image_get,CMException} requested Image doesn't exist
        """

        try:
            image = StorageImage.objects.get(pk=disk_image_id)
        except:
            raise CMException('image_get')

        return image

    # Note: disk_dev is now an integer
    def attach(self, vm):
        """
        Attaches this StorageImage to specified VM. It searches for first free
        device and if there's any, tries to attach this to it via Libvirt.
        Further it updates DB information.

        @parameter{vm,VM} instance of the existing VM

        @raises{storage_image_attach,CMException} no free device found or cannot
        attach StorageImage
        """
        domain = vm.lv_domain()
        log.debug(self.user.id, self.disk_controller)

        # Get all block devices and find first, unused sdX
        # attached_devices = [d.disk_dev for d in Session.query(StorageImage).filter(StorageImage.vm_id == vm.id).all()]
        attached_devices = [d.disk_dev for d in StorageImage.objects.filter(vm_id__exact=vm.id)]

        free_dev = None
        # for i in range(98, 122):
        # find the first free numbers to be given to disk volume (sda is now integer)
        for i in range(2, 12):
            if not i in attached_devices:
                free_dev = i
                break

        if free_dev == None:
            raise CMException('storage_image_attach')

        try:
            device_desc = """<disk type='file' device='disk'>
              <driver name='qemu' type='raw'/>
              <source file='%(path)s'/>
              <target dev='%(dev)s' bus='%(bus)s'/>
              <alias name='%(bus)s-%(dev)s'/>
            </disk>""" % {
                'path': self.path,
                # disk_dev name will be in format sd+letter corresponding to the number (e.g: 2->sdb)
                'dev':  'sd%s' % chr(free_dev + 98),
                'bus':  self.disk_controller_name
                }
            log.debug(self.user.id, device_desc)
            domain.attachDevice(device_desc)
        except:
            log.exception(self.user.id, 'storage attach')
            raise CMException('storage_image_attach')

        # Update database information
        self.disk_dev = free_dev
        self.vm = vm
        # self.vm_id = vm.id
        # saved later by the view function which calls 'attach'
        # self.save()

    def detach(self, vm):
        """
        Requests Libvirt to detach from given VM this StorageImage.

        @parameter{vm,VM} VM from which StorageImage should be detached.

        @raises{storage_image_detach,CMException} cannot detach StorageImage
        """
        domain = vm.lv_domain()
        try:
            device_desc = """<disk type='file' device='disk'>
            <driver name='qemu' type='raw'/>
            <source file='%(path)s'/>
            <target dev='%(dev)s' bus='%(bus)s'/>
            <alias name='%(bus)s-%(dev)s'/>
            </disk>""" % {
            'path': self.path,
            # 'dev':  self.disk_dev,
            'dev': 'sd%s' % chr(self.disk_dev + 98),
            'bus':  self.disk_controller_name
            }
            domain.detachDevice(device_desc)
        except:
            log.exception(self.user.id, 'storage detach')
            raise CMException('storage_image_detach')

        self.vm = None
        # saved later by the view function which calls 'detach'
        # self.save()

    def check_attached(self):
        if self.vm:
            raise CMException('image_attached')
