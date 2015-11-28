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

"""@package src.cm.views.user.image
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
@author Maciej Nabożny <mn@mnabozny.pl>
"""

import urllib

from cm.utils.decorators import admin_cm_log
from cm.utils.exception import CMException
from cm.utils import log
from cm.utils.threads.image import DownloadImage
from cm.models.user import User
from cm.models.system_image import SystemImage
from cm.models.storage_image import StorageImage
from cm.models.iso_image import IsoImage
from cm.models.system_image_group import SystemImageGroup
from common.states import image_access, image_states, image_types
from common.hardware import disk_filesystems, disk_controllers, video_devices, network_devices
import os
from cm.utils.threads.image import CopyImage


@admin_cm_log(log=True)
def download(caller_id, description, name, path, disk_dev, disk_controller):
    """
    Downloads Image with given path and saves it with specified name and
    description.

    @cmview_admin_cm
    @param_post{description,string}
    @param_post{name,string}
    @param_post{path,string} HTTP or FTP path to IsoImage
    @param_post{disk_dev}
    @param_post{disk_controller}
    """

    # size value is taken
    try:
        connection = urllib.urlopen(path)
        size = int(connection.info()["Content-Length"])
    except IOError:
        log.exception('Cannot find image')
        raise CMException('image_not_found')
    except KeyError:
        log.exception(caller_id, 'Cannot calculate size')
        raise CMException('image_calculate_size')

    user = User.get(caller_id)

    image = IsoImage.create(name=name, description=description, user=user, disk_dev=disk_dev,  disk_controller=disk_controller)

    try:
        image.save()
    except Exception, e:
        log.error(caller_id, "Unable to save image to DB: %s" % str(e))
        raise CMException('image_create')

    DownloadImage(image, path, size).start()


@admin_cm_log(log=False)
def get_list(caller_id):
    """
    @cmview_admin_cm
    @response{list(dict)} IsoImage.dict property for each IsoImage
    """
    # retrieve list of the type requested
    images = IsoImage.objects.exclude(state=image_states['locked'])

    return [img.dict for img in images]


@admin_cm_log(log=True)
def get_by_id(caller_id, iso_image_id):
    """
    @cmview_admin_cm
    @param_post{iso_image_id,int} id of the IsoImage to get

    @response{dict} IsoImage.dict property for requested IsoImage
    """
    return IsoImage.admin_get(iso_image_id).dict


@admin_cm_log(log=True)
def delete(caller_id, iso_image_id):
    """
    Sets IsoImage state to 'locked'.

    @cmview_admin_cm
    @param_post{iso_image_id} id of the IsoImage to delete

    @todo Should delete IsoImage and set its state to 'deleted'.
    """
    image = IsoImage.admin_get(iso_image_id)

    image.check_attached()
    image.state = image_states['locked']
    image.save()


@admin_cm_log(log=True)
def edit(caller_id, iso_image_id, name, description, disk_controller):
    """
    Updates specified IsoImage's attributes.

    @cmview_admin_cm
    @param_post{iso_image_id,string} new IsoImage name
    @param_post{name,string} new IsoImage name
    @param_post{description,string} new IsoImage description
    @param_post{disk_controller} new IsoImage controller optional
    """

    image = IsoImage.admin_get(iso_image_id)

    if image.state != image_states['ok']:
        raise CMException('image_edit')

    image.name = name
    image.description = description
    image.disk_controller = disk_controller

    try:
        image.save()
    except:
        raise CMException('image_edit')


@admin_cm_log(log=True)
def copy(caller_id, src_image_id, dest_user_id):
    """
    Copies selected IsoImage to User's IsoImages pool.

    @cmview_admin_cm
    @param_post{src_image_id,int}
    @param_post{dest_user_id,int}
    """
    src_image = IsoImage.admin_get(src_image_id)
    dest_user = User.get(dest_user_id)
    dest_image = IsoImage.create(name=src_image.name, description=src_image.description, user=dest_user,
                                    disk_controller=src_image.disk_controller, disk_dev=src_image.disk_dev)

    try:
        dest_image.save()
    except Exception, e:
        log.error(caller_id, "Unable to commit: %s" % str(e))
        raise CMException('image_create')

    CopyImage(src_image, dest_image).start()
