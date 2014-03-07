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

"""@package src.common
@author Gaetano
@date Mar 18, 2013
"""

# -*- coding: utf-8 -*-
#from django.core import serializers
#import json
#from django.db.models.query import QuerySet

import logging
log = logging.getLogger(__name__)
#from django.http import HttpResponse


def response(status, data=''):
    """
    Returns dictionary which is the response for the request.
    The dictionary contains 2 keys: status and data.
    """
    d = {}
    d['status'] = status
    d['data'] = data
    return d
