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

"""@package src.ec2.key_pair
EC2 actions for key pairs

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

from ec2.base.action import Action, CLMException
from ec2.error import InvalidKeyPair, MissingParameter, InvalidFilter
from ec2.helpers.filters import applyEc2Filters, validateEc2Filters
from ec2.helpers.parse import parseFilters, parseSequenceArguments

class CreateKeyPair(Action):
    def _execute(self):
        try:
            key_name = self.parameters['KeyName']
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])
        try:
            id_rsa = self.cluster_manager.user.key.generate({'name':key_name})
        except CLMException, error:
            if error.status == 'ssh_key_already_exist':
                raise InvalidKeyPair.Duplicate(key_name=key_name)
            raise error
        key_pair = self.cluster_manager.user.key.get({'name':key_name})
        return {
            'keyFingerprint': key_pair['fingerprint'],
            'keyMaterial': id_rsa,
            'keyName': key_name,
        }


class DeleteKeyPair(Action):
    def _execute(self):
        try:
            key_name = self.parameters['KeyName']
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])
        try:
            self.cluster_manager.user.key.delete({'name':key_name})
        except CLMException, error:
            pass # Amazon does not handle NotFound error here.


class DescribeKeyPairs(Action):

    translation_filters = {'key-name' : 'name',
                           'fingerprint' : 'fingerprint'}

    available_filters = ['key-name', 'fingerprint']

    def _execute(self):
        key_names = parseSequenceArguments( self.parameters, prefix = 'KeyName.' )

        filters = parseFilters( self.parameters )
        if not validateEc2Filters( filters, self.available_filters ):
            raise InvalidFilter

        key_pairs = []
        if key_names:
            for key_name in key_names:
                key_pairs.append( self.cluster_manager.user.key.get({'name':key_name}) )
        else:
            key_pairs = self.cluster_manager.user.key.get_list();
#             key_pairs = self.cluster_manager.send_request("/user/key/get_list/")
#             key_pairs = self.cluster_manager.key.user.list()

        result = []

        for key_pair in key_pairs:
#             if not key_names or key_pair in key_names:
            result.append({'key-name' : key_pair['name'],
                       'fingerprint' : key_pair['fingerprint']
                       })


        result = applyEc2Filters( result, filters )

        print 'result:',result
        return {
            'key_pairs': result
        }


class ImportKeyPair(Action):# TODO
    def _execute(self):
        import base64
        try:
            key_name = self.parameters['KeyName']
            id_rsa_pub = base64.b64decode(self.parameters['PublicKeyMaterial'])
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])
        try:
            self.cluster_manager.user.key.add({'key': id_rsa_pub, 'name': key_name})
        except CLMException, error:
            raise error
        key_pair = self.cluster_manager.user.key.get({'name' : key_name})
        return {
            'keyFingerprint': key_pair['fingerprint'],
            'keyName': key_name,
        }