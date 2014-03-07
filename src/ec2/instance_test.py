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

"""@package src.ec2.instance_test

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

from xmlrpclib import DateTime

from ec2.base.action import Action
from ec2.base.test import TestCase


class InstanceTestCase(TestCase):

    def test_DescribeInstances(self):
        self.cluster_manager.vm.user.list.return_value = [{
            'id': '1234',
            'priv_ip': '5.6.7.8',
            'pub_ip': '1.2.3.4',
            'state': 1,
            'user_id': '5678',
        },]
        self.cluster_manager.vm.user.get_by_id.return_value = {
            'id': '1234',
            'image_name': 'test image',
            'priv_ip': '5.6.7.8',
            'pub_ip': '1.2.3.4',
            'state': 1,
            'start_time': DateTime('20121015T16:10:00'),
            'user_id': '5678',
        }

        response = Action({
            'Action': 'DescribeInstances',
        }, self.cluster_manager).execute()
        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <DescribeInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2012-06-01/">
              <requestId>00000000-0000-0000-0000-000000000000</requestId> 
              <reservationSet>
                <item>
                  <reservationId>r-00000000</reservationId>
                  <ownerId>5678</ownerId>
                  <instancesSet>
                    <item>
                      <hypervisor>kvm</hypervisor>
                      <imageId>test image</imageId>
                      <instanceId>1234</instanceId>
                      <instanceState>
                        <code>16</code>
                        <name>running</name>
                      </instanceState>
                      <instanceType>m1.small</instanceType>
                      <ipAddress>1.2.3.4</ipAddress>
                      <launchTime>2012-10-15T16:10:00</launchTime>
                      <placement>
                        <availabilityZone>test_cm</availabilityZone>
                      </placement>
                      <privateIpAddress>5.6.7.8</privateIpAddress>
                      <reason></reason>
                    </item>
                  </instancesSet>
                </item>
              </reservationSet>
            </DescribeInstancesResponse>
            """
        )

    def test_TerminateInstances(self):
        self.cluster_manager.vm.user.destroy.return_value = None

        response = Action({
            'Action': 'TerminateInstances',
            'InstanceId.1': '1',
        }, self.cluster_manager).execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <TerminateInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2012-06-01/">
              <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId> 
              <instancesSet>
                <item>
                  <instanceId>1</instanceId>
                  <currentState>
                    <code>32</code>
                    <name>shutting-down</name>
                  </currentState>
                  <previousState>
                    <code>16</code>
                    <name>running</name>
                  </previousState>
                </item>
              </instancesSet>
            </TerminateInstancesResponse>
            """
        )
