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

"""@package src.ec2.image_test
@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

from ec2.base.action import Action
from ec2.base.test import TestCase


class ImageTestCase(TestCase):

    def test_DescribeImages(self):
        self.cluster_manager.image.user.list.side_effect = [
            [{
                'description': 'Fake image 01.',
                'id': 123,
                'name': 'image 01',
                'platform': 2,
                'state': 0,
                'user_id': 1,

            }],
            [{
                'description': 'Fake image 02.',
                'id': 456,
                'name': 'image 02',
                'platform': 2,
                'state': 0,
                'user_id': 1,
            }],

        ]
        action = Action({'Action': 'DescribeImages'}, self.cluster_manager)
        response = action.execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <DescribeImagesResponse xmlns="http://ec2.amazonaws.com/doc/2012-03-01/">
              <requestId>833f0802-7b29-4641-b953-6f6b78908b22</requestId>
              <imagesSet>
                <item>
                  <architecture>x86_64</architecture>
                  <description>Fake image 01.</description>
                  <imageId>123</imageId>
                  <imageLocation>ami-123</imageLocation>
                  <imageState>available</imageState>
                  <imageOwnerId>1</imageOwnerId>
                  <isPublic>false</isPublic>
                  <name>image 01</name>
                  <platform></platform>
                </item>
                <item>
                  <architecture>x86_64</architecture>
                  <description>Fake image 02.</description>
                  <imageId>456</imageId>
                  <imageLocation>ami-456</imageLocation>
                  <imageState>available</imageState>
                  <imageOwnerId>1</imageOwnerId>
                  <isPublic>true</isPublic>
                  <name>image 02</name>
                  <platform></platform>
                </item>
              </imagesSet>
            </DescribeImagesResponse>
            """
        )
