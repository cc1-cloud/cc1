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
from ec2.error import InsufficientAddressCapacity, MissingParameter, \
    UndefinedError, InvalidInstanceID, InvalidAddress, InvalidIPAddress, \
    InternalError, InvalidParameterValue, InvalidFilter
from ec2.helpers.entities import Entity
from ec2.helpers.filters import applyEc2Filters, validateEc2Filters
from ec2.helpers.parse import parseSequenceArguments, parseFilters, \
    parseID

"""@package src.ec2.address

EC2 actions for IP addresses

@author: Oleksandr Gituliar <oleksandr@gituliar.org>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
@copyright: Copyright (c) 2012 IFJ PAN <http://www.ifj.edu.pl/>
"""


class AllocateAddress(Action):
    def _execute(self):
        try:
            address = self.cluster_manager.user.public_ip.request()
        except CLMException, error:
            if error.status == 'public_lease_limit':
                raise InsufficientAddressCapacity()
            if error.status == 'public_lease_request':
                raise InternalError
            raise UndefinedError
        return {'publicIp': address}


class AssociateAddress(Action):
    def _execute(self):
        try:
            instance_id = parseID(self.parameters['InstanceId'], Entity.instance)
            if not instance_id:
                raise InvalidParameterValue
            instance_id = int(instance_id)

            public_ip = self.parameters['PublicIp']
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])
        except ValueError, error:
            raise InvalidInstanceID.Malformed(image_id=instance_id)

        addresses = self.cluster_manager.user.public_ip.get_list()
        for address in addresses + [None]:
            if address and address['address'] == public_ip:
                break
        if not address:
            raise InvalidAddress.NotFound

        lease_id = None
        instances = self.cluster_manager.user.vm.get_list()
        for instance in instances:
            if instance['vm_id'] == instance_id:
                print instance['leases'][0]
                lease_id = instance['leases'][0]['lease_id']
        if not lease_id:
            raise InvalidInstanceID.NotFound(image_id=instance_id)

        try:
            none = self.cluster_manager.user.public_ip.assign(
                {'lease_id': lease_id, 'public_ip_id': address['public_ip_id']}
            )
        except CLMException, error:
            if error.status == 'public_lease_assigned':
                raise InvalidIPAddress.InUse
            print 'NIE PRZECHWYCONY WYJATEK', error.status
            raise UndefinedError

        return None


class DescribeAddresses(Action):

    available_filters = ['instance-id', 'public-ip']

    def _execute(self):

        public_ips = parseSequenceArguments(self.parameters, prefix='PublicIp.')

        filters = parseFilters(self.parameters)
        filters_ok = validateEc2Filters(filters, self.available_filters)
        if not filters_ok:
            raise InvalidFilter

        result = []

        addresses = self.cluster_manager.user.public_ip.get_list()
        if public_ips:
            addresses = [address for address in addresses if address['address'] in public_ips]
        for address in addresses:
            vm_id = None
            lease_id = address['lease_id']
            if lease_id:
                instances = self.cluster_manager.user.vm.get_list()
                for instance in instances:
                    for lease in instance['leases']:
                        if lease['lease_id'] == lease_id:
                            vm_id = instance['vm_id']
                            break
            result.append({
                'domain': 'standard',
                'instance-id': vm_id,
                'public-ip': address['address'],
            })

        result = applyEc2Filters(result , filters)

        return {'addresses': result}


class DisassociateAddress(Action):
    def _execute(self):
        try:
            public_ip = self.parameters['PublicIp']
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])

        addresses = self.cluster_manager.user.public_ip.get_list()
        lease_id = None
        for address in addresses:
            if address['address'] == public_ip:
                lease_id = address['lease_id']
                break
        if not lease_id:
            # TODO Handle error when IP address is not associated with any instance. TODO
            # Don't know which amazon's error should be used
            raise UndefinedError

        none = self.cluster_manager.user.public_ip.unassign({'lease_id':lease_id})

        return None


class ReleaseAddress(Action):
    def _execute(self):
        try:
            public_ip = unicode(self.parameters['PublicIp'])
        except KeyError:
            raise MissingParameter(parameter='PublicIp')
        print type(public_ip)

        addresses = self.cluster_manager.user.public_ip.get_list()

        return_address = {}
        return_address['address'] = -1
        for address in addresses :
            if address.get('address') == public_ip:
                return_address = address

        if return_address['address'] == -1:
            raise InvalidAddress.NotFound

        # TODO sprawdzic czy tu nie trzeba sprawdzac wyjatkow
        none = self.cluster_manager.user.public_ip.release({'public_ip_id':return_address['public_ip_id']})

        return None
