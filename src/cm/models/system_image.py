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

"""@package src.cm.models.system_image
"""

import os
import random
import subprocess
import time

from django.conf import settings, settings as django_settings
from django.db import models
from django.template import loader, Context

from cm.models.image import Image
from cm.utils import log
from cm.utils.exception import CMException
from common.hardware import video_devices, network_devices, \
    video_devices_reversed, network_devices_reversed
from common.states import image_access
from cm.utils import message


class SystemImage(Image):
    """
    @model{SYSTEM_IMAGE} VM type image's class.

    System image is one of the Images type. SystemImage class extends
    src.cm.models.image.Image class.
    By default virtual machine boots from copy of the stored VM image.
    At the VM's creation moment it's required to choose one VM image

    We can distinguish:
    - public images
    - private images
    - group images

    VM images are mutable while VM is running. When closing VM, the copy
    of the image that virtual machine is running from may be saved to
    private images' pool.

    Despite the ability of VM images to store data it's not their purpose.
    It is far more convenient and recommended to store data on
    Storage Images (StorageImages).
    """
    platform = models.IntegerField()

    # default values are taken from hardware.py
    network_device = models.IntegerField(default=network_devices['virtio'])
    video_device = models.IntegerField(default=video_devices['cirrus'])

    @classmethod
    def create(cls, name, description, user, platform, disk_controller, network_device, video_device):
        image = Image.create(cls, name=name, description=description, user=user, size=0, progress=0,
                             disk_dev=1, disk_controller=disk_controller)
        image.platform = platform
        image.access = image_access['private']
        image.network_device = network_device
        image.video_device = video_device
        return image

    # TODO: is vms and user_group necessary too?
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
            d['disk_dev'] = 'sd%s' % chr(self.disk_dev + 96)
        else:
            d['disk_dev'] = ''

        # fields for vm image:
        d['user_id'] = self.user.id
        d['access'] = self.access
        d['disk_controller'] = self.disk_controller
        d['platform'] = self.platform
        d['system_image_id'] = self.id

        # TODO:
        # set of vms with this image attached
        d['vms'] = list(self.vm_set.filter(state__in=[vm_states['running'], vm_states['running_ctx']]).values_list('id', flat=True)) or []

        # groups image belongs (only one group for now)
        grouplist = self.systemimagegroup_set.values_list('group_id', flat=True)
        d['group_id'] = grouplist[0] if len(grouplist) > 0 else ''

        d['disk_controller'] = self.disk_controller
        d['video_device'] = self.video_device
        d['network_device'] = self.network_device

        return d

    @staticmethod
    def get(user_id, sys_image_id, groups=None):
        """
        Method returns requested VMImage, provided specified User actually
        has right to access it:
        - either as it's owner,
        - or as member of a Group VMImage belongs to.

        @parameter{user_id,int} User for whom VMImage should be obtained
        @parameter{sys_image_id,int} id of the requested VMImage
        @parameter{groups,list(int)} ids of the Groups that User belongs to @optional{None}

        @returns{Image} requested VMImage instance, provided specified User
        actually has right to access it

        @raises{image_get,CMException} no such VMImage
        """

        try:
            image = SystemImage.objects.get(pk=sys_image_id)
        except:
            raise CMException('image_get')

        image.has_access(user_id, groups)
        return image

    @staticmethod
    def admin_get(sys_image_id):
        """
        Getter, which should be called by admin. It doesn't check Image's ownership.

        @parameter{sys_img_id,int} primary index of the @type{VMImage}

        @returns{SystemImage} instance of @type{SystemImage} based on primary index provided

        @raises{image_get,CMException}
        """

        try:
            image = SystemImage.objects.get(pk=sys_image_id)
        except:
            raise CMException('image_get')

        return image

    def has_access(self, user_id, groups=None):
        """
        @parameter{user_id,int} id of the User to check for right to access
        @parameter{groups,list(int)} id if the Groups User belongs to; required
        if Image's access type is 'group'

        @returns{bool}
        True, if specified User or listed Groups have right to access this
        Image. Otherwise exception is thrown.

        @raises{system_image_permission,CMException} neither User nor listed Groups
        have right to access this Image.
        """
        if self.user.id != user_id:
            if self.access == image_access['private']:
                raise CMException('image_permission')
            elif self.access == image_access['group'] and ((groups is None) or (not(self.systemimagegroup_set.filter(group_id__in=groups).exists()))):
                raise CMException('image_permission')
        return True

    @property
    def video_device_name(self):
        """
        Method filters VIDEO_DEVICES list to find video device name by
        the video_device id that is assigned to this Image.
        @returns{string} name of this Image's the video device, if such a
        video device exists. otherwise 'vga'
        """
        try:
            return video_devices_reversed[self.video_device]
        except Exception:
            log.error(self.user.id, 'Cannot find video device')
            return 'vga'

    @property
    def network_device_name(self):
        """
        Method filters NETWORK_DEVICES list to find network device name by
        the network_device id with is assigned to this Image.
        @returns{string} name of this Image's network device, if such a
        network device exists.
        """
        try:
            return network_devices_reversed[self.network_device]
        except Exception:
            log.error(self.user.id, 'Cannot find network device')

    # Create temporary Libvirt Pool description to copy from/to images.
    # storage and user parameters are used to define storage path
    # create django template rendered with image context
    # method called only by 'copy_to_node' and  'copy_to_storage'
    def prepare_temporary_pool_xml(self, image):
        """
        Create temporary Libvirt Pool description to copy from/to images.
        storage and user parameters are used to define storage path

        @raises{cm_template_create,CMException}
        """
        try:
            django_settings.configure()
        except Exception:
            pass

        try:
            # Open template file
            template = open("%s/storage_dir.xml" % settings.TEMPLATE_DIR).read()
            # Create django template
            st_template = loader.get_template_from_string(template)
            c = Context({'parent_pool': image.storage.name, 'user': image.user.id, 'cc_userid': 331, 'cc_groupid': 331})
            t = st_template.render(c)
            log.info(self.user.id, "Rendered template: %s" % t)
        except Exception, e:
            log.exception(self.user.id, "Cannot create template: %s" % str(e))
            raise CMException('cm_template_create')
        return t

    # not used
    def wait_pool_is_unused(self, conn, pool_name):
        for i in range(60):
            try:
                conn.storagePoolLookupByName(pool_name)
                log.debug(self.user_id, "Waiting for pool...")
                time.sleep(10 * random.random())
            except Exception:
                log.debug(self.user_id, "Pool doesn't exists")
                break

    def copy_to_node(self, vm):
        """
        Copy vm image from storage to node

        @raises{vm_create,CMException}
        """
        r = subprocess.call(['ssh', vm.node.ssh_string, 'chmod a+rw %s' % (vm.system_image.path)])

        log.debug(vm.user.id, "Copy image by ssh")
        log.debug(vm.user.id, str(['ssh', vm.node.ssh_string, 'cp %s /images/%d' % (vm.system_image.path, vm.id)]))

        if subprocess.call(['ssh', vm.node.ssh_string, 'cp %s /images/%d' % (vm.system_image.path, vm.id)]):
            message.error(vm.user_id, 'vm_create', {'id': vm.id, 'name': vm.name})
            raise CMException('vm_create')

        if subprocess.call(['ssh', vm.node.ssh_string, 'chmod a+rw /images/%d' % vm.id]):
            message.error(vm.user_id, 'vm_create', {'id': vm.id, 'name': vm.name})
            raise CMException('vm_create')
        return

    def copy_to_storage(self, vm, image):
        """
        Copy vm image from node images pool to selected image on storage. Image
        entity should be createt before calling this function
        """
        log.debug(vm.user.id, "Preparing temporary storage pool")
        if not os.path.exists(os.path.dirname(image.path)):
            os.makedirs(os.path.dirname(image.path))
        log.debug(vm.user.id, str(['ssh', vm.node.ssh_string, 'cp /images/%d %s' % (vm.id, image.path)]))

        if subprocess.call(['ssh', vm.node.ssh_string, 'cp /images/%d %s' % (vm.id, image.path)]):
            raise CMException('image_copy_to_storage')
