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

"""@package src.ec2.base.auth
Signature generators for EC2 API requests
@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Rafał Grzymkowski
@author Miłosz Zdybał
"""

import base64
import hashlib
import hmac
import urllib


def authorize_ec2_request(parameters, aws_secret_key, **kwargs):
    """Authorize EC2 API request by comparing generated and request signatures."""
    signature_version = parameters.get('SignatureVersion')

    if signature_version == '1':
        sign_parameters = _sign_parameters_ver1
    elif signature_version == '2':
        sign_parameters = _sign_parameters_ver2
    else:
        raise Exception("Unknown SignatureVersion: %s." % signature_version)

    correct_signature = sign_parameters(
        parameters,
        aws_secret_key,
        endpoint=parameters['Endpoint'],
        method=parameters['Method'],
    )
    request_signature = parameters.get('Signature')
    return correct_signature == request_signature


def _sign_parameters_ver1(parameters, aws_secret_key, **kwargs):
    """Generate signature deoending on parameters and password (once again)."""
    #password = self.server.unsafe_ec2_gethash(parameters.get('AWSAccessKeyId'))
    params = ''
    for key in sorted(parameters.iterkeys(), key=str.lower):
        if key == 'Signature' or key == 'Method' or key == 'Endpoint':
            pass
        else:
            params += str(key)
            params += str(parameters.get(key))
    h = hmac.new(aws_secret_key, params, hashlib.sha1)
    signature = h.digest()
    signature = base64.b64encode(signature)
    return signature


def _sign_parameters_ver2_milosz(parameters, aws_secret_key, **kwargs):
    """Method generating signature deoending on parameters and password.

    Author: Miłosz Zdybał
    """
    params = {
        'Action' : parameters.get('Action'),
        'AWSAccessKeyId' : parameters.get('AWSAccessKeyId'),
        'Timestamp' : parameters.get('Timestamp'),
        'Version': parameters.get('Version'),
        'SignatureMethod' : parameters.get('SignatureMethod'),
        'SignatureVersion' : parameters.get('SignatureVersion')
    }
    string_to_sign = '%s\n%s\n/\n' % (
        parameters.get('Method'), parameters.get('Endpoint')
    )
    keys = params.keys()
    keys.sort()
    pairs = []
    for key in keys:
        val = params[key].encode('utf-8')
        pairs.append(
            urllib.quote(key, safe='') + '=' + urllib.quote(val, safe='-_~')
        )
    qs = '&'.join(pairs)
    string_to_sign += qs
    h = hmac.new(aws_secret_key, string_to_sign, hashlib.sha256)
    b64 = base64.b64encode(h.digest())
    return b64


def _sign_parameters_ver2(parameters, aws_secret_key, endpoint=None,
                          method=None):
    """Method generating signature deoending on parameters and password
    (one that checks whether it works)

    Author: Rafał Grzymkowski
    """
    toSign = '%s\n%s\n/\n' % (
        parameters.get('Method', method),
        parameters.get('Endpoint', endpoint).lower(),
    )
    keys = parameters.keys()
    keys.sort()
    pairs = []
    for key in keys:
        val = parameters[key].encode('utf-8')
        if key == 'Signature' or key == 'Method' or key == 'Endpoint':
            continue
        pairs.append(urllib.quote(key, safe='') + '=' + urllib.quote(val, safe='-_~'))
    qs = '&'.join(pairs)
    toSign += qs
    h = hmac.new(aws_secret_key, toSign, hashlib.sha256)
    b64 = base64.b64encode(h.digest())
    return b64
