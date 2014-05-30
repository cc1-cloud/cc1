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
import os
from ec2.base.s3action import S3Action
from ec2.helpers.auth import authenticate

"""@package src.s3bucket
S3 base action

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


class ListBucket(S3Action):
    def _execute(self):
        print 'ListBucket'
        authenticate(self.parameters)
        bucket = self.bucket_name
        print self.path
        if not os.path.exists(self.path):  # TODO przenieść to do innych funkcji
            os.mkdir(self.path)

        return {'body': {'bucket': bucket}}
