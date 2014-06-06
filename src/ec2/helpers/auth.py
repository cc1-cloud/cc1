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

"""@package src.helpers.s3action
Decorator for authenticating S3 requests

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""
import os
from common.utils import ServerProxy
from ec2.base.action import CLMException
from ec2.error import AuthFailure, InvalidAccessKeyId
from ec2.settings import CLM_ADDRESS, BUCKETS_PATH

CLM_AUTHENTICATE = '/guest/user/check_signature/'


def authenticate(parameters):
    clm = ServerProxy(CLM_ADDRESS)

    temp_input = parameters['input']
    temp_file_wrapper = parameters['file_wrapper']

    del parameters['input']
    del parameters['file_wrapper']

    data = {'parameters': parameters}
    response = clm.send_request(CLM_AUTHENTICATE, **data)
    status = response['status']

    print response

    if status != 'ok':
        raise AuthFailure()

    parameters['input'] = temp_input
    parameters['file_wrapper'] = temp_file_wrapper

    user_name = parameters['authorization'].split(' ')[1].split(':')[0]
    print 'Username:', user_name
    if user_name.find('..') != -1:
        raise InvalidAccessKeyId

    bucket_path = os.path.join(BUCKETS_PATH, user_name)
    print 'Bucket path:', bucket_path

    if not os.path.exists(bucket_path): # TODO przenieść to do innych funkcji
        print 'User\'s directory does not exists, creating'
        os.mkdir(bucket_path)

    print 'Authentication process successful'
    return True