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

"""@package src.ec2.helpers.parse

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

from ec2.error import InvalidFilter
from entities import Entity
from fnmatch import fnmatch

filtersTranslation = {
                      'key-name' : 'name',
                      'fingerprint' : 'fingerprint',
                      'state' : 'state',
                      'description' : 'description', # TODO ominac powtarzajace sie wartosci
                      'image-id' : 'imageId',
                      'instance-id' : 'instanceId',
                      'name' : 'name',
                      'status': 'status',
                      'size' : 'size'
                      }

prefixes = {
            'instance-id' : Entity.instance,
            'image-id': Entity.image,
            'reservation-id' : Entity.reservation,
            'volume-id' : Entity.volume
            }

def validateEc2Filters( filters, available_filters ):
    """
    Validates EC2 filters by checking if there is no unsupported filter provided by user
    and translates keys to CC1 ones
    If there is an extra filter InvalidFilter exception is raised

    @raises{InvalidFilter,EC2Exception}
    
    @parameter{filters, dict} Dictionary of filters provided by user
    @parameter{available_filters, dict} List of filters supported by server
    
    @returns{boolean} Returns True if filters are valid
    """
    
    for ec2filter in filters.keys():
        if ec2filter not in available_filters:
            return False
#         translatedFilters[ available_filters[ec2filter] ] = filters[ec2filter]
        
    return True

def applyEc2Filters( objects, filters ):
    """
    Applies EC2 Filters generated by src.restapi.ec2.helpers.parse.parseFilters
    
    @returns{list} Returns list of filtered objects
    """
    try:
        for filter_name in filters.keys():
            # tu by się przydał elegantszy sposób
            for filter_value in filters[filter_name]:
                extra_prefix = ""
                for prefix in prefixes.iteritems():
                    if filter_name == prefix[0]:
                        extra_prefix = prefix[1] + '-'
                        break
                    
                objects =  [item for item in objects if fnmatch( extra_prefix + str(item[filter_name]), filter_value) ]
#             objects =  [item for item in objects if str(item[ filtersTranslation[ filter_name ] ]) in filters[ filter_name] ]
    except KeyError, error:
        raise InvalidFilter
    
    return objects