#!/usr/bin/env python2.7
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

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

import logging
import select
from socket import gaierror, gethostbyname
from wsgiref.simple_server import make_server

from ec2.main import CloudManager, application
from ec2.settings import XMLRPCSERVER


def serve(host='localhost', port=8080, verbosity='DEBUG'):
    """Start EC2 server."""

    logging.basicConfig(level=verbosity)

    addr = gethostbyname(host)
    server = make_server(host, port, application)
    logging.info("Listen %s:%s ..." % (host, port))

    regions = CloudManager(XMLRPCSERVER).cluster_managers()
    logging.info("Available CMs: %s" % regions)

    try:
        server.serve_forever()
    except select.error, error:
        pass
    except KeyboardInterrupt, error:
        pass

if __name__ == '__main__':
    serve()
