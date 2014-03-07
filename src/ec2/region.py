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
# from common.helper import find, memoize
from ec2.base.action import Action
from ec2.error import UndefinedError, MissingParameter
from ec2.helpers.parse import parseFilters
from ec2.helpers.filters import applyEc2Filters

"""@package src.ec2.region
EC2 actions for regions

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


def getClusterManagers(endpoint , cluster_manager):
    try:
        base_URL = endpoint.split('.', 1)[1]
    except IndexError:
        raise UndefinedError

    cluster_managers = cluster_manager.cloud_manager.cluster_managers()

    return {
        'cms': [{
            'address': "%s.%s" % (cm.name, base_URL),
            'name': cm.name,
        } for cm in cluster_managers]
    }


class DescribeRegions(Action):

    def _execute(self):
        try:
            filters = parseFilters(self.parameters)

            endpoint = self.parameters.get('Endpoint')
        except KeyError:
            raise MissingParameter(parameter='Endpoint')

        cms = getClusterManagers(endpoint, self.cluster_manager)

        cms = applyEc2Filters(cms, filters)

        return cms


class DescribeAvailabilityZones(Action):
    def _execute(self):  # TODO wspieranie filtrów
        try:
            endpoint = self.parameters.get('Endpoint')
        except KeyError:
            raise MissingParameter(parameter='Endpoint')

        return getClusterManagers(endpoint, self.cluster_manager)
