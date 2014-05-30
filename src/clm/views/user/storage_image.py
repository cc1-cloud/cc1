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

"""@package src.clm.views.user.image
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from clm.models.user import User
from clm.models.group import Group
from clm.models.user_group import UserGroup
from common.states import image_access, image_types, group_states
from clm.utils.decorators import user_log, cm_request
from clm.utils.cm import CM
from clm.utils.exception import CLMException
import json
# from common import response


@user_log(log=False, pack=False)  # false
@cm_request
def get_list(cm_response, **data):
    """
    Method returns list of images.

    @parameter{data,dict}
    \n fields as described by src.cm.views.user.image.list()

    @returns{list(dict)}
    images: {gid, name, [images]}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):  # @todo rename for fun name consistency
    """
    @parameter{id,int} managed image's id
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @parameter{id,int} managed image's id
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def edit(cm_response, **data):
    """
    @parameter{id,int} managed image's id
    @parameter{data,dict}
    \n fields:
    @dictkey{name,string}
    @dictkey{description,string}
    - platform
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def create(cm_response, **data):
    """
    @parameter{data,dict}
    \n fields:
    @dictkey{size,int}
    - type
    - access
    @dictkey{user_id,int}
    @dictkey{name,string}
    @dictkey{description,string}
    @dictkey{platform} optional
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def download(cm_response, **data):
    """
    @parameter{data,dict}
    \n fields:
    - path
    - type
    @dictkey{access} optional (default: private)
    - name
    - description
    - platform
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def attach(cm_response, **data):  # @todo rename for fun name consistency
    """
    @parameter{data,dict}
    \n fields:
    @dictkey{vm_id,int} id of virtual machine
    @dictkey{img_id,int} id of block device (should be storage type)
    @dictkey{destination,string} bus type (default: scsi)
    @dictkey{check,bool} whether function should check if BD is alredy attached to VM (used only by vm.create!)
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def detach(cm_response, **data):  # @todo rename for fun name consistency
    """
    @parameter{data,dict}
    \n fields:
    @dictkey{vm_id,int}
    @dictkey{img_id,int}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_filesystems(cm_response, **data):
    """
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_disk_controllers(cm_response, **data):
    """
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def convert_to_system_image(cm_response, **data):
    """
    """
    return cm_response
