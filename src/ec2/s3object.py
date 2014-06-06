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

import hashlib
import os
from ec2.base.s3action import S3Action
from ec2.settings import BUCKETS_PATH
from ec2.helpers.auth import authenticate

"""@package src.s3object
S3 base actions for objects

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

BLOCK_SIZE = 65536

class PutObject(S3Action):
    def _execute(self):
        print 'PutObject'
        authenticate(self.parameters)
        try:
            new_file = open(os.path.join(self.path, ), 'wb')

            m = hashlib.md5()
            while True:
                chunk = self.parameters['input'].read(128)

                if not chunk:
                    break

                m.update(chunk)
                new_file.write(chunk)

            new_file.close()
            response = {'headers': [('ETag', '"' + m.hexdigest() + '"')], 'body': ''}

            return response
        except Exception, error:
            print error

class GetObject(S3Action): #TODO zabezpieczenia
    def _execute(self):
        print 'GetObject'
        file_path = self.parameters['Path_info']

        if file_path.startswith('/'):
            file_path = file_path[1:]

        image_file = open( os.path.join(BUCKETS_PATH, file_path), 'r')

        if 'File_wrapper' in self.parameters:
            return {'body': self.parameters['File_wrapper'](image_file, BLOCK_SIZE)}
        else:
            return {'body': iter(lambda: image_file.read(BLOCK_SIZE), '')}
