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
WSGI application for EC2 API service
@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

import logging
import os
import sys
import traceback
import urlparse

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
)
from ec2.settings import CLM_ADDRESS
from common.utils import ServerProxy
from ec2 import (address, image, instance, key_pair, region,
    security_group, volume, universal)
from ec2.base.action import Action, CLMException
from ec2.error import AuthFailure, EC2Exception, InvalidZone
# from restapi.ec2.settings import XMLRPCSERVER

DEBUG = True

# Validate response against Amazon EC2 XML Schema?
if False:
    import lxml.etree
    from StringIO import StringIO
    xmlschema = lxml.etree.XMLSchema(file='./restapi/ec2/base/ec2.xsd')
    def validate(response):
        doc = lxml.etree.parse(StringIO(response))
        try:
            xmlschema.assertValid(doc)
            print "Validation [PASS]"
        except lxml.etree.DocumentInvalid, error:
            print "Validation [FAIL]", error
        return response
else:
    def validate(response):
        return response
# musisz ustawiac cm_id w request


class CloudManager(object): # TODO JAK KTOS PODA ZLEGO CM TO WYWALA BLAD BRZYDKI

    def __init__(self, uri, aws_key=None, parameters=None, signature=None):
        self.aws_key = aws_key
        self.parameters = parameters
        self.signature = signature

        self._cluster_managers_data = None
        self._proxy_server = ServerProxy(uri)

    # @memoize
    def cluster_managers(self):
        if not self._cluster_managers_data:
            self._cluster_managers_data = \
                self._proxy_server.send_request("guest/cluster/list_names/")['data']

        print self._cluster_managers_data
        cluster_managers = []
        for cluster_manager_data in self._cluster_managers_data:
            cluster_manager = ClusterManager(
                cluster_manager_data['cluster_id'],
                cluster_manager_data['name'],
                self
            )
            cluster_managers.append(cluster_manager)
        return cluster_managers

    def get_cluster_manager(self, by_environ=None, by_id=None, by_name=None):
        if by_environ:
            name = by_environ['HTTP_HOST'].split('.')[0]
            cluster_manager = self.get_cluster_manager(by_name=name)
        else:
            if by_id:
                for cm in self.cluster_managers():
                    if cm.id == by_id:
                        cluster_manager = cm
                        break
            elif by_name:
                for cm in self.cluster_managers():
                    if cm.name == by_name:
                        cluster_manager = cm
                        break

        return cluster_manager


class ClusterManager(object):

    def __init__(self, id_, name, cloud_manager):
        self.cloud_manager = cloud_manager
        self.id = id_
        self.name = name

        self._rest_url = []

#     def __call__(self, *args):
    def __call__(self, data=None):
#         rpc_args = [
#             self.id,
#             self.cloud_manager.aws_key,
#             self.cloud_manager.signature,
#             ]+ list(args) +[
#             self.cloud_manager.parameters,
#         ]
        if not data:
            data = {}

        data['parameters'] = self.cloud_manager.parameters

        data['login'] = self.cloud_manager.aws_key
        data['Signature'] = self.cloud_manager.signature
#         url_to_call = self.cloud_manager._proxy_server
#         for module in self._path_to_rpc_routine:
#             url_to_call = getattr(url_to_call, module)
        url = '/' + '/'.join(self._rest_url) + '/'

        self._rest_url = []

        clm = self.cloud_manager._proxy_server

        # TODO dopisanie parametrow cm, auth itd!!!!!!!!!!!!!!!!!!!
#         data = {'arg1':'war1'}
#         status, result = clm.send_request(url, data)
        print url
        if data is not None:
            response = clm.send_request(url, **data)
        else:
            response = clm.send_request(url)
        status = response['status']
        response_data = response['data']

        if status != 'ok':
            raise CLMException(status, url, response_data)
        return response_data

    def __getattr__(self, name):
        self._rest_url.append(name)
        return self

    def __repr__(self):
        return "<ClusterManager(id=%s, name=%s)>" % (self.id, self.name)
def _environ_to_parameters(environ):
    """Extract EC2 parameters from GET/POST request.

    Args:
        environ <> WSGI's environment variable

    Returns:
        <dict> EC2 action's parameters
    """
    method = environ['REQUEST_METHOD']
    if method == 'GET':
        query_string = environ['QUERY_STRING']
    elif method == 'POST':
        query_string = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0)))
    else:
        raise Exception('Unsupported request method: %s' % method)

    parameters = {}
    for key, value in urlparse.parse_qs(query_string).iteritems():
        parameters[key] = value if len(value) != 1 else value[0]
    parameters['Endpoint'] = environ['HTTP_HOST']
    parameters['Method'] = method

    # do usuniecia
    print parameters

    return parameters


def _application(environ, start_response):
    """WSGI application for EC2 API service."""

    parameters = _environ_to_parameters(environ)
    cloud_manager = CloudManager(
        CLM_ADDRESS,
        aws_key=parameters.get('AWSAccessKeyId'),
        parameters=parameters,
        signature=parameters.get('Signature'),
    )
    cluster_manager_name = environ['HTTP_HOST'].split('.')[0]
    cluster_manager = cloud_manager.get_cluster_manager(
        by_name=cluster_manager_name
    )
    try:
        if not cluster_manager:
            raise InvalidZone.NotFound(zone_name=cluster_manager_name)
        action = Action(parameters, cluster_manager)
        response = action.execute()
        start_response('200 OK', [('Content-Type', 'text/xml;charset=UTF-8')])
    except EC2Exception, error:
        http_code = '400 Bad Request'
        if isinstance(error, AuthFailure):
            http_code = '401 Unauthorized'
        response = error.to_xml()
        start_response(http_code, [('Content-Type', 'text/xml;charset=UTF-8')])
    # TODO:
    #   * respect 'Accept-Encoding' HTTP header, i.e. gzip response, etc.
    return validate(response)


def application(environ, start_response):
    try:
        return _application(environ, start_response)
    except Exception, error:
        logging.exception(error)
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
