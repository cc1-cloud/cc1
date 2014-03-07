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

"""@package src.ec2.region_test

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

from __future__ import with_statement

import mock
import unittest


from ec2.base.action import Action
from ec2.base.test import TestCase
from ec2.main import ClusterManager


class RegionTestCase(TestCase):

    def test_DescribeAddresses(self):
        self.cluster_manager.cloud_manager.cluster_managers.return_value = [
            ClusterManager(1, 'ifj', self.cluster_manager),
            ClusterManager(2, 'agh', self.cluster_manager),
        ]

        response = Action({
            'Action': 'DescribeRegions',
            'Endpoint': 'ifj.ec2.localhost',
        }, self.cluster_manager).execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <DescribeRegionsResponse xmlns="http://ec2.amazonaws.com/doc/2012-04-01/">
               <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId>
               <regionInfo>
                  <item>
                     <regionName>ifj</regionName>
                     <regionEndpoint>ifj.ec2.localhost</regionEndpoint>
                  </item>
                  <item>
                     <regionName>agh</regionName>
                     <regionEndpoint>agh.ec2.localhost</regionEndpoint>
                  </item>
               </regionInfo>
            </DescribeRegionsResponse>
            """
        )
