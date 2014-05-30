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

"""@package src.ec2.error
EC2 API exceptions

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

from ec2 import lookup

class EC2Exception(BaseException):
    """Superclass for EC2 API exceptions."""

    def __init__(self, **context):
        """Store `context` used to build an error `message` in `to_xml`."""
        self.context = context

    def to_xml(self):
        """Return XML with error details compatible with Amazon EC2 WSDL."""
        template = lookup.get_template('error.xml')
        return template.render(
            code=self.code,
            message=self.message % self.context,
        )

class AuthFailure(EC2Exception):
    code = "AuthFailure"
    message = "AWS was not able to validate the provided access credentials."
    #The address '%(address)s' does not belong to you

class InsufficientAddressCapacity(EC2Exception):
    code = "InsufficientAddressCapacity"
    message = "Not enough available addresses to satisfy your minimum request."

class InvalidAction(EC2Exception):
    code = "InvalidAction"
    message = "The action %(action)s is not valid for this web service."

class InvalidAMIID(object):
    class NotFound(EC2Exception):
        code = "InvalidAMIID.NotFound"
        message = "The AMI ID '%(image_id)s' does not exist"
    class Malformed(EC2Exception):
        code = "InvalidAMIID.Malformed"
        message = "Specified AMI ID is malformed"
    class Unavailable(EC2Exception):
        code = "InvalidAMIID.Unavailable"
        message = "Specified AMI is temporarily unavailable"

class InvalidInstanceID(object):
    class Malformed(EC2Exception):
        code = "InvalidInstanceID.Malformed"
        message = "The Instance ID '%(image_id)s' is not valid"
    class NotFound(EC2Exception):
        code = "InvalidInstanceID.NotFound"
        message = "The Instance ID '%(image_id)s' does not exist"

class InvalidKeyPair(object):
    class Duplicate(EC2Exception):
        code = "InvalidKeyPair.Duplicate"
        message = "The keypair '%(key_name)s' already exists."
    class NotFound(EC2Exception):
        code = "InvalidKeyPair.NotFound"
        message = "The key pair '%(key_name)s' does not exist"

class InvalidZone(object):
    class NotFound(EC2Exception):
        code = "InvalidZone.NotFound"
        message = "The zone '%(zone_name)s' does not exist."

class MissingParameter(EC2Exception):
    code = "MissingParameter"
    message = "The request must contain the parameter %(parameter)s"

class UndefinedError(EC2Exception):
    code = "UndefinedError"
    message = "There is no dedicated error to describe this situation. Contact developers if you need more information."


class UnknownParameter(EC2Exception):
    code = "UnknownParameter"
    message = "The parameter %(parameter)s is not recognized"

# Łukasz Chrząszcz : Amazon
class VolumeInUse(EC2Exception):
    code = "VolumeInUse"
    message = "Specified volume is attached to VM"

class InvalidVolume(object):
    class NotFound(EC2Exception):
        code = "InvalidVolume"
        message = "Specified volume does not exist"

class InvalidVolumeID(object):
    class Duplicate(EC2Exception):
        code = ""
        message = ""
    class Malformed(EC2Exception):
        code = "InvalidVolumeID.Malformed"
        message = "Specified Volume ID is malformed, use only digits"

class DiskImageSizeTooLarge(EC2Exception):
    code = "DiskImageSizeTooLarge"
    message = "Quota exceeded"

class InvalidParameterValue(EC2Exception):
    code = "InvalidParameterValue"
    message = "A value specified in a parameter is not valid"

class InvalidParameter(EC2Exception):
    code = "InvalidParameter"
    message = "Invalid parameter"

class InternalError(EC2Exception):
    code = "InternalError"
    message = "An internal error has occurred. Try again later. If the problem persists, contact administrator"

class InvalidAddress(object):
    class NotFound(EC2Exception):
        code = "InvalidAddress.NotFound"
        message = "Couldn't find specified Elastic IP address"

class CannotDelete(EC2Exception):
    code = "CannotDelete"
    message = "Can't delete default security group"

class InvalidGroup(object):
    class NotFound(EC2Exception):
        code = "InvalidGroup.NotFound"
        message = "The specified security group does not exist"

class InvalidIPAddress(object):
    class InUse(EC2Exception):
        code = "InvalidIPAddress"
        message = "Specified IP Address is already in use. You must first disassociate it from the instance"

class InvalidFilter(EC2Exception):
    code = "InvalidFilter"
    message = "The specified filter is not correct or it is not supported"

class InvalidID(EC2Exception):
    code = "InvalidID"
    message = "The specified ID for resource is not valid"

class InvalidAttachment(object):
    class NotFound(EC2Exception):
        code = "InvalidAttachment"
        message = "Volume not attached"

class ResourceLimitExceeded(EC2Exception):
    code = "ResourceLimitExceeded"
    message = "You've exceeded limit assigned to your account. Exceeded limit: %(resource)s"

# =================== S3 Errors ===================

class MethodNotAllowed(EC2Exception):
    code = "MethodNotAllowed"
    message = "The specified method is not allowed for given resource"

class InvalidArgument(EC2Exception):
    code = "InvalidArgument"
    message = "The specified argument is not valid"

class InvalidURI(EC2Exception):
    code = "InvalidURI"
    message = "Couldn't parse the specified URI"

class InvalidAccessKeyId(EC2Exception):
    code = "InvalidAccessKeyId"
    message = "The access key ID you provided is not valid"

class InvalidManifest(EC2Exception):
    code = "InvalidManifest"
    message = "The specified manifest is unparsable"
