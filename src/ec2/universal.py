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
from ec2.base.action import Action, CLMException
from ec2.error import MissingParameter, InvalidAMIID, InvalidParameterValue, \
    InvalidInstanceID, InvalidVolumeID, InvalidVolume, InvalidFilter, InvalidID, \
    UnknownParameter
from ec2.helpers.entities import Entity
from ec2.helpers.filters import validateEc2Filters
from ec2.helpers.parse import parseFilters, parseSequenceArguments, parseID
from ec2.helpers.query import get_instance_tags, get_volume_tags, \
    get_volume_name_tag, get_instance_name_tag

"""@package src.ec2.universal
EC2 actions common for more than one resource

@copyright Copyright (c) 2014 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


class CreateTags(Action):
    def _execute(self):
        resource_ids = []
        tags = []
        try:

            for param, value in self.parameters.iteritems():
                if param.startswith('ResourceId'):
                    resource_ids.append(value)
                elif param.startswith('Tag.') and param.endswith('Key'):
                    tag_value = self.parameters.get('Tag.' + param[4:-4] + '.Value')
                    if value != 'Name':
                        raise InvalidParameterValue
                    if not tag_value:
                        raise MissingParameter(parameter='Tag.' + param[4:-4] + '.Value')
                    tags.append({'Name': tag_value})
        except KeyError:
            raise MissingParameter(parameter='ImageId') # TODO
        except ValueError:
            raise InvalidAMIID.Malformed

        for resource in resource_ids:
            if resource.startswith('vol-'):
                for tag in tags:
                    try:
                        volume = self.cluster_manager.user.storage_image.get_by_id({'storage_image_id':resource[4:]})
                    except CLMException,error :
                        raise InvalidVolume.NotFound

                    self.cluster_manager.user.storage_image.edit({'storage_image_id':resource[4:],
                                                              'name' : tag['Name'],
                                                              'description' : volume['description'],
                                                              'disk_controller' : volume['disk_controller']})
            elif resource.startswith('i-'):
                for tag in tags:
                    try:
                        instance = self.cluster_manager.user.vm.get_by_id({'vm_id': resource[2:]})
                    except CLMException, error:
                        raise InvalidInstanceID.NotFound(image_id=resource)

                    self.cluster_manager.user.vm.edit({'vm_id': resource[2:],
                                                       'name' : tag['Name'],
                                                       'description' : instance['description']})
            else:
                raise InvalidParameterValue

        # we don't return anything, in this point the only value might be True and it's coded within template


class DescribeTags(Action):

    available_filters = ['key', 'resource-id', 'resoure-type', 'value']

    def _execute(self):
        if self.parameters.get('MaxResults'):
            raise UnknownParameter(parameter='MaxResults')

        if self.parameters.get('NextToken'):
            raise UnknownParameter(parameter='NextToken')

        filters = parseFilters(self.parameters)
        if not validateEc2Filters(filters, self.available_filters):
            raise InvalidFilter

        tags = []

        if filters:
            INSTANCES = False
            VOLUMES = False

            if filters.get('key'):
                for key in filters['key']:
                    if key != 'Name':
                        raise InvalidFilter #TODO
                del filters['key']

            if filters.get('resource-id'):
                for filter in filters['resource-id']:
                    if filter.startswith('vol-') and (not filters.get('resource-type') or filters.get('resource-type') == 'volume'):
                        tags.append(get_volume_name_tag(self.cluster_manager, filter[4:]))
                    elif filter.startswith('i-') and (not filters.get('resource-type') or filters.get('resource-type') == 'instance'):
                        tags.append(get_instance_name_tag(self.cluster_manager, filter[2:]))
            elif filters.get('resource-type'):
                for filter in filters['resource-type']:
                    if filter == 'instance':
                        tags.append(get_instance_tags(self.cluster_manager))
                    elif filter == 'volume':
                        tags.append(get_volume_tags(self.cluster_manager))
                del filters['resource-type']
            else:
                tags = get_instance_tags(self.cluster_manager) + get_volume_tags(self.cluster_manager)

            if filters.get('value'):
                tags = [tag for tag in tags if tag['value'] in filters['value']]

        else: # jeżeli nie podano zadnych filtrów to zwracamy wszystkie
            tags = get_instance_tags(self.cluster_manager) + get_volume_tags(self.cluster_manager)

        return {'tags':tags}


class DeleteTags(Action):
    def _execute(self):
        resourceIds = parseSequenceArguments(self.parameters, 'ResourceId.')
        tagNames = parseSequenceArguments(self.parameters, 'Tag.', '.Key')
        tagValue = self.parameters.get('Tag.0.Value')

        if not resourceIds:
            raise MissingParameter(parameter='ResourceId.X')

        if not tagNames:
            raise MissingParameter(parameter='Tag.X.Key')

        if len(tagNames) != 1:
            raise InvalidFilter

        if tagNames[0] != 'Name':
            raise InvalidFilter

        # here we have only one tag called Name
        # TODO checking if tagValue was given
        for resource in resourceIds:

            if resource.startswith('i-'):
                instance_id = parseID(resource, Entity.instance)
                if not instance_id:
                    raise InvalidInstanceID.Malformed
                try:
                    instance = self.cluster_manager.user.vm.get_by_id({'vm_id':instance_id})
                except CLMException, error:
                    raise InvalidInstanceID.NotFound(image_id=instance_id)

                if tagValue and tagValue != 'i-' + instance['vm_id']:
                    continue
                self.cluster_manager.user.vm.edit({'vm_id' : instance_id, 'name' : 'i-' + instance_id, 'description':instance['description']})

            elif resource.startswith('vol-'):
                volume_id = parseID(resource, Entity.volume)
                if not volume_id:
                    raise InvalidVolumeID.Malformed

                try:
                    volume = self.cluster_manager.user.storage_image.get_by_id({'storage_image_id':volume_id})
                except CLMException, error:
                    raise InvalidVolume.NotFound()

                if tagValue and tagValue != 'vol-' + volume['storage_image_id']:
                    continue

                self.cluster_manager.user.storage_image.edit({'storage_image_id' : volume_id,
                                                              'name' : 'vol-' + volume_id,
                                                              'description':volume['description'],
                                                              'disk_controller':volume['disk_controller']})

            else:
                pass #TODO

        return
