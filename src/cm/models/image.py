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

"""@package src.cm.models.image

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <mn@mnabozny.pl>
"""

from datetime import datetime

from django.db import models
from django.template import loader, Context

from cm.models.storage import Storage
from cm.models.user import User
from cm.utils import log
from cm.utils.exception import CMException
from common.hardware import disk_controllers, disk_controllers_reversed
from common.states import image_states, storage_states, image_access
import libvirt
import os

from typedmodels import TypedModel


class Image(TypedModel):
    """
    abstract @model{IMAGE} Basic class for all of Image types.

    Images are files that should be considered as virtual disks attachable
    to Virtual Machines.
    CC1 images are divided into 3 groups:
    - VM images (sytem_image)
    - Storage images (disk_volune),
    - Iso images (iso_image).

    @note
    1. default values put in the fields definition of the model, not __init__
    2. getStorage operation,to initialize storage field, is now in image.utils.create(), not __init__
    3. disk_dev is now an integer, in dict is put as a string, ex: sda, if the value is 1
    4. no 'get method' because Image is abstract class, it is defined for the subclasses
    5. 'path method' defined in subclasses
    6. 'has_access method' put in system_image and iso_images (they can be in groups)

    """
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=512)
    user = models.ForeignKey(User)

    # NOTE: disk_dev is now an integer
    disk_dev = models.IntegerField(null=True, blank=True)
    disk_controller = models.IntegerField(default=disk_controllers['scsi'])
    # creation_date is datetime.now by default
    creation_date = models.DateTimeField(default=datetime.now)
    size = models.IntegerField(null=True, blank=True)
    state = models.SmallIntegerField()
    storage = models.ForeignKey(Storage, null=True, blank=True)
    progress = models.IntegerField(default=100)
    access = models.SmallIntegerField()

    class Meta:
        app_label = 'cm'

    @staticmethod
    def create(cls, name, description, user, disk_dev, disk_controller, size=0, progress=100):
        image = cls()
        image.name = name
        image.description = description
        image.state = image_states['adding']
        image.user = user
        image.size = size
        image.progress = progress
        image.disk_dev = disk_dev
        image.storage = Storage.get()
        image.disk_controller = disk_controller
        image.access = image_access['private']
        return image

    # method for printing object instance
    def __unicode__(self):
        return self.name

    # @property
    # method used by the subclasses, it put in dict the fields common to all images
    def dictImg(self):
        """
        @returns{dict} image's data
        \n fields:
        @dictkey{id}
        @dictkey{user_id,int}
        @dictkey{name}
        @dictkey{description}
        @dictkey{creation_date}
        @dictkey{progress}
        @dictkey{state}
        @dictkey{size}
        """
        d = {}
        d['image_id'] = self.id
        d['user_id'] = self.user.id
        d['name'] = self.name
        d['description'] = self.description
        d['disk_controller'] = self.disk_controller

        # disk_dev put in dict of subclasses
        # d['disk_dev'] = self.disk_dev

        d['creation_date'] = self.creation_date
        d['progress'] = self.progress

        # Image's state depends on storage's state (storage could be unavailable
        if self.storage is None or self.storage.state != storage_states['ok']:
            d['state'] = image_states['unavailable']
        else:
            d['state'] = self.state

        if self.size is not None:
            d['size'] = self.size
        else:
            d['size'] = 0

        return d

    def set_state(self, state):
        """
        @parameter{state,string} slug name of the new state for this Image

        @raises{vm_wrong_state,CMException} such a state doesn't exist
        """

        # Key - destination state
        # Values - actual available states
        states = {'init': (),
            'adding': ('init'),
            'failed': ('init', 'adding', 'formatting', 'ok', 'unavailable', 'locked', 'deleted'),
            'formatting': ('adding'),
            'ok': ('formatting', 'adding', 'locked'),
            'unavailable': (),
            'locked': ('ok'),
            'deleted': ('ok', 'locked', 'failed'),
            }

        # Find my state:
        my_state = False
        for s in image_states.keys():
            if self.state == image_states[s]:
                my_state = s

        if self.storage.state == storage_states['locked']:
            if state == 'adding' or state == 'formatting':
                raise CMException('vm_wrong_state')

        # Check if Image could go from actual state to given
        if not my_state in states[state] or my_state == False:
            raise CMException('vm_wrong_state')

    @property
    def path(self):
        """
        #@returns{string} path to image
        """
        img_path = '%d' % self.id
        log.info(self.user.id, 'Storage: %s, user_id: %d, image_id: %s' % (self.storage.path, self.user.id, img_path))
        return os.path.join(self.storage.path, str(self.user.id), img_path)

    @property
    def disk_controller_name(self):
        """
        Method filters DISK_CONTROLLERS list to find controller name by
        the disk_controller id with is assigned to this Image.
        @returns{string} name of this Image's disk controller, if
        such a controller exists
        """
        try:
            return disk_controllers_reversed[self.disk_controller]
        except Exception:
            log.error(self.user.id, 'Cannot find disk controller')
