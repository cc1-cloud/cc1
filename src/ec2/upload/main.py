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

"""@package src.ec2.upload
WSGI application for publishing system images for CLM/CM to download

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""
import logging
import os
import traceback
import urlparse
from ec2.settings import UPLOAD_IMAGES_PATH
import sys

DEBUG = True

QUERY_IMAGE_NAME = 'image_name'
BLOCK_SIZE = 65536

logging.basicConfig(stream=sys.stdout)
logging.basicConfig(stream=sys.stderr)


def _environ_to_parameters(environ):
    """Extract EC2 parameters from GET/POST request.

    Args:
        environ <> WSGI's environment variable

    Returns:
        <dict> EC2 action's parameters
    """
    query_string = environ['QUERY_STRING']

    query_string_params = urlparse.parse_qs(query_string)
    if len(query_string_params) != 1:
        pass  # ERROR

    parameters = {}
    parameters['image_name'] = query_string_params['image_name'][0]

    # we keep blank values to capture commands for S3

    print 15 * '=', 'PARAMETERS', 15 * '='
    for u, v in parameters.iteritems():
        print u, ":", v
    print 42 * '='

    return parameters


def application(environ, start_response):
    print 15 * '=', 'EC2-CM-UPLOAD', 15 * '='
    try:
        # return _application(environ, start_response)
        parameters = _environ_to_parameters(environ)

        image_name = parameters[QUERY_IMAGE_NAME]
        file_path = os.path.join(UPLOAD_IMAGES_PATH, image_name)

        image_file = open(file_path, 'r')
        start_response('200 OK', [])
        if 'wsgi.file_wrapper' in environ:
            return environ['wsgi.file_wrapper'](image_file, BLOCK_SIZE)
        else:
            return iter(lambda: image_file.read(BLOCK_SIZE), '')

    except Exception, error:
        response = handle_500(environ, error)
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return response


def handle_500(environ, error):
    if DEBUG:
        response = traceback.format_exc()
        print response
    else:
        response = '500 Internal Server Error'
    return response
