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

"""@package src.ec2
EC2 actions for security groups

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

from ec2.base.action import Action
from ec2.error import CannotDelete, InvalidGroup, MissingParameter


# We don't support security groups, but some scripts and applications
# use them, so when required we return default security group
class DescribeSecurityGroups(Action):
    def _execute(self):
        return None  # default values are returned by xml template


class DeleteSecurityGroup(Action):
    def _execute(self):
        try:
            group_name = self.parameters['GroupName']
        except KeyError, error:
            raise MissingParameter(parameter=error.args[0])

        if group_name == 'default':
            raise CannotDelete

        # if group_name is not default then raise error, because there's no way to create other group :D
        raise InvalidGroup.NotFound
