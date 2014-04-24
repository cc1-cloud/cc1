# _*_ coding: utf_8 _*_
# @COPYRIGHT_begin
#
# Copyright [2010_2013] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE_2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end
"""@package src.cm.manager.ec2ctx.helpers.request

@copyright Copyright (c) 2013 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""

from cm.models.vm import VM
from cm.utils import log
from cm.utils.exception import CMException
from time import sleep


def get_vm_by_ip(vm_ip):
#     vm = None
#     counter = 0
#     while (not vm and counter < 10):
#         try:
#             counter += 1
#             vm = VM.get_by_ip(vm_ip)
#         except CMException,error:
#             log.error(0, "Couldn't get vm by it's ip: %s: %s. Retrying" % (vm_ip, error.message))
#             sleep(2)
#             vm = None
#     if not vm:
#         log.error(0, "Couldn't get vm by it's ip: %s: %s" % (vm_ip, error.message))
#         raise cherrypy.HTTPError(500)
#
#     return vm
    pass
