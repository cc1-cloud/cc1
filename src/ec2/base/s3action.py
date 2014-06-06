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
from ec2 import lookup
from ec2.base.action import Action, CLMException
from ec2.error import InvalidAction, MethodNotAllowed, InvalidArgument, InvalidURI, EC2Exception
from ec2.settings import BUCKETS_PATH

"""@package src.base.s3action
S3 base action

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

class S3Action(object):
    """Superclass for S3 API actions."""

    def __init__(self, parameters):
        self.parameters = parameters
        path = self.parameters['path_info']

        user_name = self.parameters['authorization'].split(' ')[1].split(':')[0]
        path = user_name + '/' + path

        if path.find('..') != -1:
            raise InvalidURI

        path = os.path.normpath(path)  # is it required?

        if path.startswith('/'):
            path = path[1:]

        slash = path.find('/')
        if slash != -1:
            bucket_name = path[:slash + 1]
        else:
            bucket_name = path

        normpath = os.path.join(BUCKETS_PATH, path)

        self.path = normpath
        self.bucket_name = bucket_name

    def __new__(cls, parameters):
        """Return an object of a concrete S3 action class.

        Args:
            parameters <dict> of the action
            cluster_manager <ClusterManager> the action will be run at
        """
        concrete_class = None
        if cls == S3Action:
            if parameters['query_string']:
                raise MethodNotAllowed()

            path = os.path.normpath(parameters['path_info'])
            if path.startswith('/'):
                path = path[1:]
            if path.endswith('/'):
                path = path[:-1]

            path_parts = path.split('/')

            if len(path_parts) == 1:  # bucket
                if parameters['request_method'] == 'GET' or parameters['request_method'] == 'HEAD':
                    concrete_class_name = 'ListBucket'
            else:
                if parameters['request_method'] == 'PUT':
                    concrete_class_name = 'PutObject'
                if parameters['request_method'] == 'GET':
                    concrete_class_name = 'GetObject'

            for concrete_class in cls.__subclasses__():
                if concrete_class.__name__ == concrete_class_name:
                    break
        else:
            concrete_class = cls

        action = super(S3Action, cls).__new__(concrete_class, parameters)
        action.concrete_class_name = concrete_class_name
        return action


    def _get_template(self):
        name = '%s.xml' % self.concrete_class_name
        return lookup.get_template(name)

    def execute(self):
        context = self._execute()

        # if body is dict then parse it to xml
        if context['body'].__class__ is dict:
            template = self._get_template()
            response = template.render(**context['body'])
        else:
            # if it isn't dict then pass that object directly
            response = context['body']

        result = {'body': response,
                  'headers': context.get('headers')}

        return result
