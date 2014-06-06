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

"""@package src.common.Signature
Signatures handling for EC2 API for CC1

@author Rafal Grzymkowski
@author Miłosz Zdybał
"""

import base64
import hashlib
import hmac
import logging
import urllib


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class Signature:
    """
    """
    def __init__(self):
        """
        """
        self.signature = "%s\n%s\n%s\n" % ('POST', 'ec2.us-east-1.amazonaws.com', '/')

    @staticmethod
    def generateSignatureVer2(password, parameters):
        """
        Method generating signature deoending on parameters and password (one that checks whether it works)

        Version 2
        """
        toSign = parameters.get('Method') + '\n' + parameters.get('Endpoint').lower() + '\n' + '/\n'
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
        h = hmac.new(password, toSign, hashlib.sha256)
        b64 = base64.b64encode(h.digest())

        return b64

    @staticmethod
    def generateSignatureVer1(password, parameters):
        """
        Method generating signature deoending on parameters and password (once again).

        Version 1
        """
        params = ''
        for key in sorted(parameters.iterkeys(), key=str.lower):
            if key == 'Signature' or key == 'Method' or key == 'Endpoint':
                pass
            else:
                params += str(key)
                params += str(parameters.get(key))
        h = hmac.new(password, params, hashlib.sha1)
        signature = h.digest()
        signature = base64.b64encode(signature)
        return signature

    @staticmethod
    def checkSignature(password, signatureToCheck, parameters):
        """
        Check, whether signature is correct (depending on the signature's version).
        """
        version = int(parameters.get('SignatureVersion'))
        correctSignature = None
        if version == 1:
            correctSignature = Signature.generateSignatureVer1(str(password), parameters)
        elif version == 2:
            correctSignature = Signature.generateSignatureVer2(str(password), parameters)
        return True if correctSignature == signatureToCheck else False
