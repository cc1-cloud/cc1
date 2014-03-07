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

"""@package src.ec2.helpers.query

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

from datetime import datetime
import urllib

from ec2.base.auth import _sign_parameters_ver2


def query(parameters, aws_key=None, aws_secret=None, endpoint=None,
          method=None, secure=False):
    parameters.setdefault('SignatureMethod', 'HmacSHA256')
    parameters.setdefault('SignatureVersion', '2')

    parameters['AWSAccessKeyId'] = aws_key
    #parameters['Expires'] = "2012-03-17T12:41:35Z"
    parameters['Timestamp'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    parameters['Version'] = "2012-03-01"

    # set Signature
    signature = _sign_parameters_ver2(
        parameters,
        aws_secret,
        endpoint=endpoint,
        method=method,
    )
    parameters['Signature'] = signature

    # build request
    protocol = 'http' if not secure else 'https'
    query_parameters = urllib.urlencode(parameters)
    if method == 'GET':
        request = ("%s://%s/?%s" % (protocol, endpoint, query_parameters),)
    elif method == 'POST':
        request = ("%s://%s" % (protocol, endpoint), query_parameters)
    else:
        raise Exception('Unsupported %s method: %s' % (protocol.upper(), method))

    response = urllib.urlopen(*request).read()

    return request, response
