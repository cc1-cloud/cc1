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

"""@package src.ec2.address_test

@author Oleksandr Gituliar <gituliar@gmail.com>
@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
"""

from __future__ import with_statement

import mock

from ec2.base.action import Action
from ec2.error import AuthFailure, UndefinedError
from ec2.base.test import TestCase


class AddressTestCase(TestCase):

    def test_AllocateAddresses(self):
        self.cluster_manager.elasticip.user.request.return_value = {
            'ip': '1.1.0.1',
        }

        action = Action({'Action': 'AllocateAddress'}, self.cluster_manager)
        response = action.execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <AllocateAddressResponse xmlns="http://ec2.amazonaws.com/doc/2012-03-01/">
               <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId> 
               <publicIp>1.1.0.1</publicIp>
               <domain>standard</domain>
            </AllocateAddressResponse>
            """
        )

    def test_AssociateAddress(self):
        self.cluster_manager.elasticip.user.assign.return_value = None
        self.cluster_manager.elasticip.user.list.return_value = [
            {'ip_id': 1,'vm_id': 1, 'ip': '1.1.0.1'},
            {'ip_id': 2,'vm_id': None, 'ip': '1.1.0.2'},
        ]

        action = Action({
            'Action': 'AssociateAddress',
            'InstanceId': 2,
            'PublicIp': '1.1.0.2',
        }, self.cluster_manager)
        response = action.execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <AssociateAddressResponse xmlns="http://ec2.amazonaws.com/doc/2012-03-01/">
              <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId>
              <return>true</return>
            </AssociateAddressResponse>
            """
        )

        with self.assertRaises(AuthFailure):
            action = Action({
                'Action': 'AssociateAddress',
                'InstanceId': 2,
                'PublicIp': '1.1.0.3'
            }, self.cluster_manager)
            response = action.execute()

    def test_DescribeAddresses(self):
        self.cluster_manager.elasticip.user.list.return_value = [
            {'vm_id': 1, 'ip': '192.168.0.1'},
            {'vm_id': None, 'ip': '192.168.0.2'},
        ]

        action = Action({'Action': 'DescribeAddresses'}, self.cluster_manager)
        response = action.execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <DescribeAddressesResponse xmlns="http://ec2.amazonaws.com/doc/2012-03-01/">
              <requestId>a13c7c2e-4106-459d-a728-9d38bcbab9bf</requestId>
              <addressesSet>
                <item>
                  <publicIp>192.168.0.1</publicIp>
                  <domain>standard</domain>
                  <instanceId>1</instanceId>
                </item>
                <item>
                  <publicIp>192.168.0.2</publicIp>
                  <domain>standard</domain>
                  <instanceId>None</instanceId>
                </item>
              </addressesSet>
            </DescribeAddressesResponse>
            """
        )

    def test_DisassociateAddress(self):
        self.cluster_manager.elasticip.user.unassign.return_value = None
        self.cluster_manager.elasticip.user.list.return_value = [
            {'ip_id': 1,'vm_id': 1, 'ip': '1.1.0.1'},
            {'ip_id': 2,'vm_id': None, 'ip': '1.1.0.2'},
        ]

        action = Action({
            'Action': 'DisassociateAddress',
            'PublicIp': '1.1.0.1'
        }, self.cluster_manager)
        response = action.execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <DisassociateAddressResponse xmlns="http://ec2.amazonaws.com/doc/2012-03-01/">
              <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId>
              <return>true</return>
            </DisassociateAddressResponse>
            """
        )

        with self.assertRaises(UndefinedError):
            response = Action({
                'Action': 'DisassociateAddress',
                'PublicIp': '1.1.0.2'
            }, self.cluster_manager).execute()

        with self.assertRaises(UndefinedError):
            response = Action({
                'Action': 'DisassociateAddress',
                'PublicIp': '1.1.0.3'
            }, self.cluster_manager).execute()

    def test_ReleaseAddress(self):
        self.cluster_manager.elasticip.user.list.return_value = [
            {'ip_id': 1,'vm_id': 1, 'ip': '1.1.0.1'},
            {'ip_id': 2,'vm_id': None, 'ip': '1.1.0.2'},
        ]
        self.cluster_manager.elasticip.user.release.return_value = {
            'status': 'ok',
            'data': None
        }

        response = Action({
            'Action': 'ReleaseAddress',
            'PublicIp': '1.1.0.1'
        }, self.cluster_manager).execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <ReleaseAddressResponse xmlns="http://ec2.amazonaws.com/doc/2012-03-01/">
              <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId> 
              <return>true</return>
            </ReleaseAddressResponse>
            """
        )

        with self.assertRaises(AuthFailure):
            response = Action({
                'Action': 'ReleaseAddress',
                'PublicIp': '1.1.0.3'
            }, self.cluster_manager).execute()