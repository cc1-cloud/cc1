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

"""@package src.cm.models.iso_image
"""

from django.db import models

from cm.models.image import Image
from cm.utils import log
from cm.utils.exception import CMException
from common.hardware import disk_controllers_reversed
from common.states import image_states, storage_states, image_access, vm_states


class IsoImage(Image):
    """
    @model{image} Class for CD Images

    CD type Image is one of the Images type. CDImage class extends
    src.cm.models.image.Image class.
    CD Images are meant to be downloaded by user from some external source and
    attached to VMs so that VMs may boot from them. Such Images are immutable.
    """

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

        if self.disk_dev is not None:
            d['disk_dev'] = 'cdrom%d' % self.disk_dev
        else:
            d['disk_dev'] = ''

        d['iso_image_id'] = self.id

        vms = self.vm_set.filter(state__in=[vm_states['running'], vm_states['running_ctx']])
        vm_ids = []
        vm_names = []
        for vm in vms:
            vm_ids.append(vm.id)
            vm_names.append(vm.name)

        d['vm_ids'] = vm_ids
        d['vm_names'] = vm_names

        return d

    @staticmethod
    def get(user_id, iso_image_id):
        """
        Method returns image \c id if it belongs to user \c user_id
        (and optionally to listed \c groups, if any given)

        @parameter{user_id,int}
        @parameter{id,int}
        @parameter{groups,list} - optional

        @returns{Image} image with id given

        @raises{image_get,CMException}
        """

        try:
            image = IsoImage.objects.get(pk=iso_image_id)
        except:
            raise CMException('image_get')

        # check on state and storage?
        if image.state != image_states['ok'] and image.storage.state != storage_states['ok']:
            raise CMException('image_unavailable')

        image.has_access(user_id)
        return image

    # @returns CDmage instance for admin user
    @staticmethod
    def admin_get(iso_image_id):
        """
        Getter, which should be called by admin. It doesn't check Image's ownership.

        @parameter{id,int} primary index of the @type{cdImage}

        @returns{StorageImage} instance of @type{StorageImage} based on primary index provided

        @raises{image_get,CMException}
        """

        try:
            image = IsoImage.objects.get(pk=iso_image_id)
        except:
            raise CMException('image_get')

        return image

    # returns True, if user \c user_id (and optionally listed \c groups)
    # has access to this image. Otherwise exception is thrown.
    def has_access(self, user_id):
        """
        @parameter{user_id,int}

        @returns{bool}
        True, if user \c user_id (and optionally listed \c groups)
        has access to this image. Otherwise exception is thrown.

        @raises{image_permission,CMException}
        """
        if self.user.id != user_id:
            if self.access == image_access['private']:
                raise CMException('image_permission')
        return True

    def check_attached(self):
        if self.vm_set.exclude(state__in=[vm_states['closed'], vm_states['erased']]).exists():
            raise CMException('image_attached')

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
        disk_controller_name = disk_controllers_reversed[self.disk_controller]

        # Get all block devices and find first, unused sdX
        # attached_devices = [d.disk_dev for d in Session.query(StorageImage).filter(StorageImage.vm_id == vm.id).all()]
        attached_devices = [d.disk_dev for d in IsoImage.objects.filter(vm_id__exact=vm.id)]

        free_dev = 'sdz'

        if free_dev == attached_devices:
            raise CMException('iso_image_attach')

        try:
            device_desc = """<disk type='file' device='disk'>
              <driver name='qemu' type='raw'/>
              <source file='%(path)s'/>
              <target dev='%(dev)s' bus='%(bus)s'/>
              <alias name='%(bus)s-%(dev)s'/>
            </disk>""" % {
                'path': self.path,
                'dev':  'sd%s' % free_dev,
                'bus':  disk_controller_name
                }
            log.debug(self.user.id, device_desc)
            domain.attachDevice(device_desc)
        except:
            log.exception(self.user.id, 'iso attach')
            raise CMException('iso_image_attach')

        # Update database information
        self.disk_dev = free_dev
        self.vm = vm

    def detach(self, vm):
        """
        Requests Libvirt to detach from given VM this StorageImage.

        @parameter{vm,VM} VM from which StorageImage should be detached.

        @raises{storage_image_detach,CMException} cannot detach StorageImage
        """
        domain = vm.lv_domain()
        disk_controller_name = disk_controllers_reversed[self.disk_controller]

        try:
            device_desc = """<disk type='file' device='disk'>
            <driver name='qemu' type='raw'/>
            <source file='%(path)s'/>
            <target dev='%(dev)s' bus='%(bus)s'/>
            <alias name='%(bus)s-%(dev)s'/>
            </disk>""" % {
            'path': self.path,
            'dev': 'sd%s' % chr(self.disk_dev + 96),
            'bus':  disk_controller_name
            }
            domain.detachDevice(device_desc)
        except:
            log.exception(self.user.id, 'iso detach')
            raise CMException('iso_image_detach')

        self.vm = None

    @classmethod
    def create(cls, name, description, user, disk_dev, disk_controller):
        image = Image.create(cls, name=name, description=description, user=user, disk_dev=disk_dev, disk_controller=disk_controller)

        return image
