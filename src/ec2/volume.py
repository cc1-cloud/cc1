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
from common.hardware import disk_filesystems, disk_controllers
from common.states import image_access, image_types
from datetime import datetime
from ec2.base.action import Action, CLMException
from ec2.error import MissingParameter, UndefinedError, InvalidVolumeID, \
    DiskImageSizeTooLarge, InvalidParameterValue, VolumeInUse, InvalidVolume, \
    InvalidInstanceID, InvalidFilter, InvalidAttachment
from ec2.helpers.entities import Entity
from ec2.helpers.filters import applyEc2Filters, validateEc2Filters
from ec2.helpers.parse import parseFilters, parseID, parseIDs, parseClmDate

"""@package src.ec2.volume
EC2 actions for volumes
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

# deleting nie jest potrzebne, bo do razu się usuwa
STATE = {
    0: 'available',  # ok
    1: 'in-use',  # locked
    2: 'creating',  # adding
    3: 'error',  # failed
    4: 'deleted',  # unavailable
}

SIZE_RATIO = 1024;  # EC2 uses GiB, we use MiB


def get_volume_status(clm_volume_state):
    if clm_volume_state == 0:
        return 'available'
    return 'failed'


class CreateVolume(Action):
    def _execute(self):
        try:
            size = int(self.parameters['Size']);
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])
        except ValueError, error:
            raise InvalidParameterValue

        ext4_id = disk_filesystems['ext4']

        volume = {}

        try:
            volume_dict = {
                        'name' : 'EC2 Volume',
                        'size' : size * SIZE_RATIO,
                        'filesystem' : ext4_id,
                        'disk_controller' : disk_controllers['virtio'],
                        'description' : 'Storage created by EC2 API'
                        }
            volume = self.cluster_manager.user.storage_image.create(volume_dict)
        except CLMException, error:
            if error.status == 'image_create':
                raise UndefinedError
            if error.status == 'user_storage_limit':
                raise DiskImageSizeTooLarge

        try:
            edit_dict = {'storage_image_id' : volume['storage_image_id'],
                         'name' : 'vol-' + str(volume['storage_image_id']),
                         'description' : 'Storage created by EC2 API',
                         'disk_controller' : disk_controllers['virtio']}

            self.cluster_manager.user.storage_image.edit( edit_dict )
        except:
            print 'Changing name for newly created storage image failed!'
            pass  # we can ignore error here, because it's not an essential operation

        return {
            'volume_id' : volume['storage_image_id'],
            'size' : size,
        }

class DescribeVolumes(Action):

    translation_filters = {'size' : 'size',
                           'volume-id' : 'volumeId',
                           'status' : 'status'}

    available_filters = ['size', 'volume-id', 'status']

    def _execute(self):
        volume_ids = []
        try:
            for param, value in self.parameters.iteritems():
                if param.startswith('VolumeId'):
                    volume_ids.append(value)
        except ValueError:
            raise InvalidParameterValue

        if volume_ids:
            volume_ids = parseIDs(volume_ids, Entity.volume)
            if not volume_ids:
                raise InvalidParameterValue

        volumes = []

        filters = parseFilters(self.parameters)
        if not validateEc2Filters(filters, self.available_filters):
            raise InvalidFilter

        # if extra arguments weren't given
        clm_volumes = []
        if not volume_ids:
            clm_volumes += self.cluster_manager.user.storage_image.get_list()

        # and if they were
        else:
            try:
                for volume_id in volume_ids:
                    clm_volumes.append(self.cluster_manager.user.storage_image.get_by_id({'storage_image_id':volume_id}))
            except CLMException, error:
                if error.status == 'image_get':
                    raise InvalidVolume.NotFound
                else:
                    raise UndefinedError

        for clm_volume in clm_volumes:
            create_time = clm_volume['creation_date']
            volume = {
                'attachTime': None,
                'createTime': parseClmDate(create_time),
                'size': clm_volume['size'] / SIZE_RATIO,
                'status': get_volume_status(clm_volume['state']),
                'volume-id': clm_volume['storage_image_id'],
            }
            volumes.append(volume)

        if filters.get('size'):
            for size in filters['size']:
                size = str(int(size) / SIZE_RATIO)

        if filters.get('status'):
            for state in filters['status']:
                state = [k for k, v in STATE.iteritems() if v == STATE.get(state) ]  # ?? wymaga testu

# attachment.attach-time - sprawdź
# attachment.delete-on-termination - ?
# attachment.device - nie
# attachment.instance-id - tak
# attachment.status - tak
# availability-zone- ?
# create-time - chyba tak
# size - TEST
# snapshot-id - nie
# status - tak TEST

# creating | available | in-use | deleting | deleted | error

# tag-key- ?
# volume-id - tak TEST
# volume-type - nie

        volumes = applyEc2Filters(volumes, filters)

        return {
            'volumes': volumes,
        }


class AttachVolume(Action):
    def _execute(self):
        try:
            try:
                volume_id_ec2 = self.parameters['VolumeId']
                volume_id = parseID(volume_id_ec2, Entity.volume)
                if not volume_id:
                    raise InvalidParameterValue
                volume_id = int(volume_id)
            except KeyError, error:
                raise InvalidVolumeID.Malformed

            try:
                instance_id_ec2 = self.parameters['InstanceId']
                instance_id = parseID(instance_id_ec2, Entity.instance)
                if not instance_id:
                    raise InvalidParameterValue
                instance_id = int(instance_id)
            except KeyError, error:
                raise MissingParameter(parameter=error.args[0])

        except ValueError, error:
            raise InvalidVolumeID.Malformed

        try:
            self.cluster_manager.user.storage_image.attach({'storage_image_id' : volume_id ,
                                                            'vm_id' : instance_id})
        except CLMException, error:
            if error.status == 'image_attached':
                raise VolumeInUse
            if error.status == 'image_get':
                raise InvalidVolume.NotFound
            if error.status == 'user_permission' or error.status == 'vm_get':
                raise InvalidInstanceID.NotFound(image_id=instance_id_ec2)

            if error.status == 'storage_image_attach':
                raise UndefinedError
            raise UndefinedError

        return {'volume_id' : volume_id_ec2,
                'instance_id' : instance_id_ec2,
                'device' : 'not implemented',
                'status' : 'attaching'}


class DetachVolume(Action):
    def _execute(self):
        try:
            volume_id = self.parameters['VolumeId']
            volume_id = parseID(volume_id, Entity.volume)
            if not volume_id:
                raise InvalidParameterValue
            volume_id = int(volume_id)
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])
        except ValueError, error:
            raise InvalidParameterValue

        instance_id_ec2 = self.parameters.get('InstanceId')
        instance_id = instance_id_ec2
        if instance_id_ec2:
            instance_id = parseID(instance_id_ec2, Entity.instance)
            if not instance_id:
                raise InvalidParameterValue
            instance_id = int(instance_id)
            try:
                self.cluster_manager.user.storage_image.detach({ 'storage_image_id' : volume_id, 'vm_id' : instance_id })
            except CLMException, error:
                if error.status == 'storage_image_detach':
                    raise UndefinedError
                if error.status == 'image_get':
                    raise InvalidVolume.NotFound
                if error.status == 'user_permission' or error.status == 'vm_get':
                    raise InvalidInstanceID.NotFound(image_id=instance_id)

        else:
            try:
                volume_dict = self.cluster_manager.user.storage_image.get_by_id({'storage_image_id':volume_id})
                if volume_dict['vm_id'] is None:
                    raise InvalidAttachment.NotFound
                self.cluster_manager.user.storage_image.detach({ 'storage_image_id' : volume_id, 'vm_id' : volume_dict['vm_id'] })
            except CLMException, error:
                if error.status == 'storage_image_detach':
                    raise UndefinedError
                if error.status == 'image_attached':
                    raise VolumeInUse
                if error.status == 'image_get':
                    raise InvalidVolume.NotFound
                if error.status == 'user_permission' or error.status == 'vm_get':
                    raise InvalidInstanceID.NotFound(image_id=instance_id)

        return {'volume_id':volume_id,
                'instance_id' : instance_id}


class DeleteVolume(Action):
    def _execute(self):
        try:
            volume_id = self.parameters['VolumeId']
            volume_id = parseID(volume_id, Entity.volume)
            if not volume_id:
                raise InvalidParameterValue
            volume_id = int(volume_id)
        except KeyError:
            raise MissingParameter(parameter='VolumeId')
        except ValueError:
            raise InvalidVolumeID.Malformed(image_id=volume_id)

        try:
            self.cluster_manager.user.storage_image.delete({'storage_image_id' : volume_id})
        except CLMException, error:
            if error.status == 'image_get' or error.status == 'image_permission':
                raise InvalidVolume.NotFound
            if error.status == 'image_attached':
                raise VolumeInUse
            raise UndefinedError

        return None
