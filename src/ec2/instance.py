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
from common.states import ec2names, vm_states, image_access
from ec2.base.action import Action, CLMException
from ec2.error import InvalidAMIID, InvalidKeyPair, MissingParameter, \
    InvalidParameterValue, InvalidInstanceID, InvalidVolumeID, InternalError, \
    UndefinedError, InvalidFilter
from ec2.helpers.entities import Entity
from ec2.helpers.filters import applyEc2Filters, validateEc2Filters
from ec2.helpers.parse import parseSequenceIntArguments, parseFilters, parseIDs, \
    parseID, parseSequenceArguments, parseClmDate

"""@package src.ec2.instance
EC2 actions for instances

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Rafał Grzymkowski
@author Miłosz Zdybał
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""




CLM_STATES = {
  0: (0, 'pending'),  # pending
  1: (16, 'running'),  # running
  2: (32, 'shutting-down'),  # closing
  3: (48, 'terminated'),  # closed
  4: (64, 'stopping'),  # saving
  5: (0, 'pending'),  # failed
  6: (0, 'pending'),  # saving failed
  7: (16, 'running'),  # running ctx
  8: (0, 'pending') ,  # restart
  10:(80, 'stopped'),  # turned off
  11:(0, 'pending'),  # erased
  12:(0, 'pending'),  # erasing
}


class DescribeInstances(Action):
    available_filters = ['image-id', 'instance-id', 'reservation-id']

    def _execute(self):

        filters = parseFilters(self.parameters)
        if not validateEc2Filters(filters, self.available_filters):
            raise InvalidFilter

        clm_instances = []

        counter = 1
        while True:  # first we parse arguments provided in request
            instance_id = self.parameters.get('InstanceId.' + str(counter) , None)

            if instance_id is None:  # if there no such argument then break
                break

            instance_id = parseID(instance_id, Entity.instance)
            if instance_id is None:
                raise InvalidParameterValue

            counter += 1
            try:
                instance = int(instance_id)
            except ValueError:
                raise InvalidParameterValue

            clm_instances.append({'vm_id':instance })

        # if we didn't provide specific IDs then use a whole list of user's VMs
        if not clm_instances:
            clm_instances = self.cluster_manager.user.vm.get_list()


        ec2_instances = []
        try:
            for clm_instance in clm_instances:
                clm_instance = self.cluster_manager.user.vm.get_by_id({'vm_id': clm_instance['vm_id']})
                if clm_instance['state'] == vm_states['closed']:
                    raise InvalidInstanceID.NotFound(image_id=clm_instance['vm_id'])
                
                privateIpAddress = None
                if clm_instance['leases']:
                    privateIpAddress = clm_instance['leases'][0].get('address')
                
                ec2_instance = {
                    'image-id': clm_instance['image_id'],
                    'instance-id': clm_instance['vm_id'],
                    'instanceState': {
                        'code': CLM_STATES[clm_instance['state']][0],
                        'name': CLM_STATES[clm_instance['state']][1]},  # TODO odpowiednia data!
                    'launchTime': parseClmDate(clm_instance['start_time']),
                    'template_name' : clm_instance['template_name'],
                    'ownerId': clm_instance['user_id'],
                    'placement': {
                        'availabilityZone': self.cluster_manager.name},
                    'privateIpAddress': privateIpAddress,
                    'reservation-id' : clm_instance['reservation_id'],
                }

                public_ip = clm_instance['leases'][0]['public_ip']
                ec2_instance['ipAddress'] = public_ip.get('ip') if public_ip else None
                ec2_instances.append(ec2_instance)
        except CLMException, error:
            if error.status == 'vm_get' or error.status == 'user_permission':
                raise InvalidInstanceID.NotFound(image_id=clm_instance['vm_id'])

        owner_id = None
        if ec2_instances:
            owner_id = ec2_instances[0]['ownerId']
# availability-zone - rozważyć
# block-device-mapping.attach-time - ?
# block-device-mapping.delete-on-termination - ?
# block-device-mapping.device-name - ?
# block-device-mapping.status - ?
# block-device-mapping.volume-id - ?
# client-token - ?
# dns-name - ?

# image-id - wspieramy - OK
# instance-id - wspieramy - OK
# instance-lifecycle - ?
# instance-state-code - możemy wspierać
# instance-state-name - będziemy wspierać
# instance-type - będziemy wspierać

# ip-address - będziemy wspierać
# key-name - ?
# launch-index - ?
# launch-time - możemy
# monitoring-state - ?
# placement-group-name - ?
# platform - możemy?
# private-ip-address - przydałoby się
# product-code - ?
# product-code.type - ?

# reason - ?

# reservation-id - ??

# tag-key - ?
# tag-value - ?
# virtualization-type - chyba mamy tlyko jeden typ
# vpc-id - ?
# hypervisor - ? chyba tylko 1

# association.public-ip - nie wiem?



        reservation_filter = None
        if filters and filters.get('reservation-id'):
            reservation_filter = {'reservation-id' : filters['reservation-id'] }
            del filters['reservation-id']

        ec2_instances = applyEc2Filters(ec2_instances , filters)


        reservationsIds = []
        for ec2_instance in ec2_instances:
            reservationId = int(ec2_instance['reservation-id'])
#             reservationId = int(ec2_instance['instance-id'])
            if reservationId not in reservationsIds:
                reservationsIds.append(reservationId)

        reservations = []
        for reservation in reservationsIds:
            reservations.append({ 'reservation-id' : reservation,
                                 'ownerId' : owner_id,
                            'instances' : [instance for instance in ec2_instances if instance['reservation-id'] == reservation]
#                               'instances' : [instance for instance in ec2_instances if instance['instance-id'] == reservation]
                              })
#
        if reservation_filter:
            reservations = applyEc2Filters(reservations , reservation_filter)



        return {'reservations' : reservations}

#         return {'instances': ec2_instances}


class RunInstances(Action):
    def _execute(self):
        try:
            image_id = self.parameters['ImageId']
            image_id = parseID(image_id, Entity.image)
            if not image_id:
                raise InvalidParameterValue

            image_id = int(image_id)
        except KeyError:
            raise MissingParameter(parameter='ImageId')
        except ValueError:
            raise InvalidAMIID.Malformed
            # raise InvalidAMIID.NotFound(image_id=image_id)

        instance_type = self.parameters.get('InstanceType', 'm1.small')
        key_name = self.parameters.get('KeyName')
        user_data = self.parameters.get('UserData', None)

        template_id = None
        for template in self.cluster_manager.user.template.get_list():
                if template.get('ec2name') == ec2names.get(instance_type):
                    dir(template)
                    template_id = int(template['template_id'])
                    break

        machine = {
            'count': int(self.parameters.get('MinCount', 1)),
            'description': 'created by EC2 API',
            'image_id': image_id,
            'name': 'noname',
            'template_id': template_id if template_id is not None else 1,
            'public_ip_id':None,
            'iso_list': None,
            'disk_list':None,
            'vnc':None,
            'user_data' : user_data
        }

        if key_name:
            try:
                key = self.cluster_manager.user.key.get({'name':key_name})
            except CLMException, error:
                if error.status == 'ssh_key_get':
                    raise InvalidKeyPair.NotFound(key_name=key_name)
            machine['ssh_key'] = key['data']
            machine['ssh_username'] = 'root'


        device_mapping_counter = 1
        volumes = []

        # EC2 passes data about volumes by BlockDeviceMapping.X.VirtualName parameter
        # where X starts with 1 and step is also 1
        while True:
            volume = self.parameters.get('BlockDeviceMapping.' +
                                   str(device_mapping_counter) +
                                   '.VirtualName')

            if volume is None:
                break

            volume = parseID(volume, Entity.volume)
            if volume is None:
                raise InvalidParameterValue

            device_mapping_counter += 1
            try:
                volumes.append(int(volume))
            except ValueError:
                raise InvalidVolumeID.Malformed

        if volumes:
            machine['disk_list'] = volumes

        instances = []



        # as far as I know here we have problem detecting if image_get regard volume or AMI
        # TODO load volumes from CLM and check on EC2 server if specified volume exists
        try:
            instances = self.cluster_manager.user.vm.create(machine)
#             instances = self.cluster_manager.vm.user.create(machine)
        except CLMException, error:
            if error.status == 'vm_create':
                raise InternalError  # we have not enough information to determine what happened
            if error.status == 'image_get' or error.status == 'image_permission':
                raise InvalidAMIID.NotFound(image_id=image_id)

            print error.status  # TODO jak sie wyjasni to sie usunie
            raise UndefinedError



        reservation_id = instances[0]['vm_id']
        instance_ids = [instance['vm_id'] for instance in instances]
        print 'instance_ids:', instance_ids

        for instance_id in instance_ids:
#             vm_desc = {
#                 'name' : 'i-' + str(instance_id),
#                 'description' : 'created by EC2 API'
#             }
            print 'editing'
            edit_response = self.cluster_manager.user.vm.edit({'vm_id': instance_id,
                                                                'name':'i-' + str(instance_id),
                                                                'description': 'created by EC2 API' })

            print edit_response
        return {
            'reservationId' : reservation_id,
            'instances': [{
                'imageId': image_id,
                'instanceId': instance_id,
                'instance_type': instance_type,
            } for instance_id in instance_ids]
        }

# create <-- [{'id':5},{'id':6},{'id':7}]


class TerminateInstances(Action):
    def _execute(self):
        instance_ids = []
        for param, value in self.parameters.iteritems():
            if param.startswith('InstanceId'):
                try:
                    value = parseID(value, Entity.instance)
                    if not value:
                        raise InvalidParameterValue
                    instance_ids.append(int(value))
                except ValueError:
                    raise InvalidInstanceID.Malformed(image_id=value)
        if not instance_ids:
            raise MissingParameter(parameter='InstanceId')

        try:
            none = self.cluster_manager.user.vm.destroy({'vm_ids': instance_ids})
        except CLMException, error:
            if error.status == 'vm_get' or error.status == 'user_permission':
                raise InvalidInstanceID.NotFound(image_id=0)  # TODO wykrywanie który instance jest zly
            print error.status
            raise InternalError  # destroy should throw no exception, however, we check and raise InternalError just in case

        return {
            'instances': [{
                'id': instance_id,
            } for instance_id in instance_ids],
        }

class RebootInstances(Action):
    def _execute(self):
        try:
            instances = parseSequenceArguments(self.parameters, 'InstanceId.')
            if not instances:
                raise MissingParameter(parameter='InstanceId')
            instances = parseIDs(instances, Entity.instance)
            if not instances:
                raise InvalidParameterValue
            # nie powinno się tutaj rzutować na inta?
        except ValueError:
            raise InvalidInstanceID.Malformed(image_id=0)  # TODO wykrywanie który instance jest zly

        try:
            none = self.cluster_manager.user.vm.reset({'vm_ids':instances })
        except CLMException, error:
            if error.status == 'user_permission' or error.status == 'vm_get':
                raise InvalidInstanceID.NotFound(image_id=0)  # TODO wykrywanie która dokładnie to instancja
            print error.status
            raise InternalError
