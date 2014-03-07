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

"""@package src.ec2.key_pair_test

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

from __future__ import with_statement

import mock

from ec2.base.action import Action, CLMException
from ec2.base.test import TestCase
from ec2.error import InvalidKeyPair, MissingParameter


class KeyPairTestCase(TestCase):

    def test_CreateKeyPair(self):
        self.cluster_manager.key.user.gen.return_value = 'key data'
        self.cluster_manager.key.user.get.return_value = {
            'fingerprint': 'fingerprint data',
        }

        # 1. Test success.
        response = Action({
            'Action': 'CreateKeyPair',
            'KeyName': 'test key pair',
        }, self.cluster_manager).execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <CreateKeyPairResponse xmlns="http://ec2.amazonaws.com/doc/2012-04-01/">
              <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId>
              <keyName>test key pair</keyName>
              <keyFingerprint>fingerprint data</keyFingerprint>
              <keyMaterial>key data</keyMaterial>
            </CreateKeyPairResponse>
            """
        )

        # 2. Test `MissingParameter`.
        with self.assertRaises(MissingParameter):
            response = Action({
                'Action': 'CreateKeyPair',
            }, self.cluster_manager).execute()


        self.cluster_manager.key.user.gen.return_value = None

        # 3. Test `InvalidKeyPair.Duplicate` exception.
        self.cluster_manager.key.user.gen.side_effect = \
            CLMException('ssh_key_already_exist', 'key.user.gen')
        with self.assertRaises(InvalidKeyPair.Duplicate):
            response = Action({
                'Action': 'CreateKeyPair',
                'KeyName': 'test key pair',
            }, self.cluster_manager).execute()


    def test_DeleteKeyPair(self):
        self.cluster_manager.key.user.delete.return_value = None

        # 1. Test success.
        response = Action({
            'Action': 'DeleteKeyPair',
            'KeyName': 'test key pair',
        }, self.cluster_manager).execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <DeleteKeyPairResponse xmlns="http://ec2.amazonaws.com/doc/2012-04-01/">
              <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId> 
              <return>true</return>
            </DeleteKeyPairResponse>
            """
        )

        # 2. Test `MissingParameter`.
        with self.assertRaises(MissingParameter):
            response = Action({
                'Action': 'DeleteKeyPair',
            }, self.cluster_manager).execute()


    def test_DescribeKeyPairs(self):
        self.cluster_manager.key.user.list.return_value = [
            {'name': 'key01', 'fingerprint': 'fp01'},
            {'name': 'key02', 'fingerprint': 'fp02'},
        ]

        # 1. Test success.
        response = Action({
            'Action': 'DescribeKeyPairs',
        }, self.cluster_manager).execute()

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <DescribeKeyPairsResponse xmlns="http://ec2.amazonaws.com/doc/2012-04-01/">
              <requestId>59dbff89-35bd-4eac-99ed-be587EXAMPLE</requestId> 
              <keySet>
                <item>
                  <keyName>key01</keyName>
                  <keyFingerprint>fp01</keyFingerprint>
                </item>
                <item>
                  <keyName>key02</keyName>
                  <keyFingerprint>fp02</keyFingerprint>
                </item>
              </keySet>
            </DescribeKeyPairsResponse>
            """
        )


    def test_ImportKeyPair(self):
        self.cluster_manager.key.user.add.return_value = None
        self.cluster_manager.key.user.get.return_value = {
            'fingerprint': 'test fingerprint',
        }

        # 1. Test success.
        response = Action({
            'Action': 'ImportKeyPair',
            'KeyName': 'test key name',
            'PublicKeyMaterial': 'test key material',
        }, self.cluster_manager).execute()

        self.cluster_manager.key.user.add.assert_called_once_with({
            'name': 'test key name',
            'key': 'test key material'
        })

        self.assertMultiLineEqual(
            response,
            """<?xml version="1.0" encoding="UTF-8"?>
            <ImportKeyPairResponse xmlns="http://ec2.amazonaws.com/doc/2012-04-01/">
               <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
               <keyName>test key name</keyName>
               <keyFingerprint>test fingerprint</keyFingerprint>
            </ImportKeyPairResponse>
            """
        )

        # 2. Test `MissingParameter`.
        with self.assertRaises(MissingParameter):
            response = Action({
                'Action': 'ImportKeyPair',
            }, self.cluster_manager).execute()

        with self.assertRaises(MissingParameter):
            response = Action({
                'Action': 'ImportKeyPair',
                'KeyName': 'test key name'
            }, self.cluster_manager).execute()

        with self.assertRaises(MissingParameter):
            response = Action({
                'Action': 'ImportKeyPair',
                'PublicKeyMaterial': 'test key material',
            }, self.cluster_manager).execute()
