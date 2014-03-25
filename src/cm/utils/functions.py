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

"""@package src.cm.utils.functions
@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <di.dijo@gmail.com>
"""
import subprocess
from cm.utils import log


def execute(command_list):
    try:
        log.debug(0, "Execute command: %s"%str(command_list))
        log_file = file('/var/log/cc1/cm_thread.log', 'a')
        r = subprocess.call(command_list, stdout=log_file, stderr=log_file)
        log_file.close()
    except Exception, e:
        log.error(0, "Execute command %s failed: %s"%(str(command_list), e))
    return r


def execute_with_output(command_list):
    try:
        log.debug(0, "Execute command (with output): %s"%str(command_list))
        p = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = p.communicate()
    except Exception, e:
        log.error(0, "Execute command (with output) %s failed: %s"%(str(command_list), e))
    return r
