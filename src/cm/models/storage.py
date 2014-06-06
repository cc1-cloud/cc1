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

"""@package src.cm.models.storage

@author Maciej Nabożny <di.dijo@gmail.com>
"""

from django.db import models
from django.db.models import Sum
from django.template import loader, Context

from cm.utils.exception import CMException
from common.states import storage_states
import libvirt


class Storage(models.Model):
    """
    @model{STORAGE} Class for storages

    This class controlls cluster's Storage - where Images are stored.
    Storage is mounted to Node physical machine via web interface.
    """
    name = models.CharField(max_length=256)
    capacity = models.IntegerField()
    state = models.IntegerField(default=0)
    address = models.CharField(max_length=64, null=True)
    dir = models.CharField(max_length=256, null=True)
    transport = models.CharField(max_length=20, default="netfs")

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return self.name

    @property
    def dict(self):
        """
        @returns{dict} this Storage's data
        \n fields:
        @dictkey{id,int}
        @dictkey{state} @seealso{src.common.states.storage_states}
        @dictkey{name,string} human-readable name of this Storage
        @dictkey{capacity,int} space total [MB] of this Storage
        @dictkey{used_space,int} space used [MB]
        @dictkey{mountpoint,string} mountpoint path to this Storage on the CM
        @dictkey{dir,string} export path on the NFC server
        @dictkey{address,string} NFC server address
        """
        d = {}
        d['storage_id'] = self.id
        d['state'] = self.state
        d['name'] = self.name
        d['capacity'] = self.capacity
        d['used_space'] = self.used_space
        d['mountpoint'] = self.path
        d['dir'] = self.dir
        d['address'] = self.address
        return d

    @property
    def path(self):
        """
        @returns{string} total mountpoint path to this Storage on the CM
        """
        try:
            conn = libvirt.open('qemu:///system')
            conn.storagePoolLookupByName(self.name)
        except:
            pass
        return '/var/lib/cc1/storages/%s/' % self.name

    @property
    def used_space(self):
        """
        Returns total size of images space (system, disks and cds) used on this Storage [MB]
        @returns{int} used space on storage
        """

        return self.image_set.aggregate(Sum('size'))['size__sum'] or 0

    @property
    def free_space(self):
        """
        @returns{int} free space on this Storage [MB]
        """
        return self.capacity - self.used_space

    @staticmethod
    def get():
        """
        Returns the Storage with the most amount of free space
        @returns{Storage} instance of Storage with the most amount of free space

        @raises{storage_no_storage,CMException} no Storages mounted
        """

        storages = Storage.objects.filter(state__exact=storage_states['ok'])

        if storages.count() == 0:
            raise CMException("storage_no_storage")

        # order storages by free_space, which is a property method, not a field
        # storages.sort(key=lambda storage: storage.free_space)
        sorted(storages, key=lambda storage: storage.free_space)

        # return the first
        return storages[0]

    def lock(self):
        """
        Method sets this Storage's state as "locked".  Nothing can be read from
        or written to this Storage. Images saved on this Storage are displayed
        on the Web Interface as unavailable.
        """
        self.state = storage_states['locked']

    def unlock(self):
        """
        Method sets this Storage's state as "ok". Storage may be used as usual.
        """
        self.state = storage_states['ok']

    def libvirt_template(self):
        template = loader.get_template("pools/%s.xml" % self.transport)
        c = Context({'storage': self,
                     'cc_userid': 331,
                     'cc_groupid': 331})
        return template.render(c)
