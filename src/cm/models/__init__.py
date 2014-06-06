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

"""@package src.cm.models
@author Gaetano
@author Maciej Nabozny
@date Mar 6, 2013

Each new entity model should be imported by this file. Also each model
should have subclass Meta with app_label='cm':

class Meta:
    app_label = 'cm'
"""

from cm.models.admin import Admin
from cm.models.available_network import AvailableNetwork
from cm.models.command import Command
from cm.models.iso_image import IsoImage
from cm.models.lease import Lease
from cm.models.node import Node
from cm.models.public_ip import PublicIP
from cm.models.storage import Storage
from cm.models.storage_image import StorageImage
from cm.models.system_image import SystemImage
from cm.models.system_image_group import SystemImageGroup
from cm.models.template import Template
from cm.models.user import User
from cm.models.user_network import UserNetwork
from cm.models.vm import VM
