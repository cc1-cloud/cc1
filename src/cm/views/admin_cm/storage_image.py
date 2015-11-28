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
    Downloads specified StorateImage from remote path.

    @cmview_admin_cm
    @param_post{description,string}
    @param_post{name,string} how to name newly downloaded storage image
    @param_post{path,string} HTTP or FTP path to download StorageImage.
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

    image = StorageImage.create(name=name, description=description, user=user, disk_dev=disk_dev,  disk_controller=disk_controller)

    try:
        image.save()
    except Exception, e:
        log.error(caller_id, "Unable to save image to DB: %s" % str(e))
        raise CMException('image_create')

    DownloadImage(image, path, size).start()


@admin_cm_log(log=False)
def get_list(caller_id):
    """
    Fetch all StorageImages except those that are @val{locked}.

    @cmview_admin_cm
    @response{list(dict)} StorageImages.dict property for each StorageImages.
    """
    # retrieve list of the type requested
    images = StorageImage.objects.exclude(state=image_states['locked'])

    return [img.dict for img in images]


@admin_cm_log(log=True)
def get_by_id(caller_id, storage_image_id):
    """
    Fetch requested StorageImage.

    @cmview_admin_cm
    @param_post{storage_image_id,int} id of the requested StorageImage

    @response{dict} StorageImages.dict property for requested StorageImage
    """
    return StorageImage.admin_get(storage_image_id).dict


@admin_cm_log(log=True)
def delete(caller_id, storage_image_id):
    """
    Sets StorageImage state as @val{locked}.

    @cmview_admin_cm
    @param_post{storage_image_id} id of the Image to delete

    @todo Should rather delete StorageImage and set its state to 'deleted'.
    """
    image = StorageImage.admin_get(storage_image_id)

    image.check_attached()
    image.state = image_states['locked']
    image.save()


@admin_cm_log(log=True)
def edit(caller_id, storage_image_id, name, description, disk_controller):
    """
    Updates Image's attributes.

    @cmview_admin_cm
    @param_post{storage_image_id,string}
    @param_post{name,string} new Image name
    @param_post{description,string} new Image description
    @param_post{disk_controller} new Image controller optional
    """

    image = StorageImage.admin_get(storage_image_id)

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
def convert_to_system_image(caller_id, storage_image_id):
    """
    Converts specified StorageImage to SystemImage. After convertion it's not
    available as StorageImage anymore. File is moved and StorageImage entry is
    removed from database.

    @cmview_admin_cm
    @param_post{storage_image_id,int} ID of an StorageImage to convert
    """
    image = StorageImage.admin_get(storage_image_id)

    system_image = SystemImage.create(name=image.name, description=image.description, user=image.user, disk_controller=image.disk_controller)
    system_image.state = image_states['ok']
    system_image.size = image.size

    try:
        system_image.save()
        os.rename(image.path, system_image.path)
        image.delete()
    except Exception:
        raise CMException('image_change_type')


@admin_cm_log(log=True)
def copy(caller_id, src_image_id, dest_user_id):
    """
    Copy selected StorageImage to user's StorageImages

    @cmview_admin_cm
    @param_post{src_image_id,int}
    @param_post{dest_user_id,int}
    """
    src_image = StorageImage.admin_get(src_image_id)
    dest_user = User.get(dest_user_id)
    dest_image = StorageImage.create(name=src_image.name, description=src_image.description, user=dest_user,
                                    disk_controller=src_image.disk_controller, size=src_image.size)

    try:
        dest_image.save()
    except Exception, e:
        log.error(caller_id, "Unable to commit: %s" % str(e))
        raise CMException('image_create')

    CopyImage(src_image, dest_image).start()
