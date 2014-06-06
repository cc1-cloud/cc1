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
    Downloads image depending on the \c data parameter.
    @cmview_admin_cm

    @parameter{description,string}
    @parameter{name,string}
    @parameter{path,string} HTTP or FTP path to image to download
    @parameter{type,image_types} type of image, automatically set, type is in the URL requested

    @response{None}
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
    Returns images.
    @cmview_admin_cm

    @parameter{access} ( image_access['group'] | image_access['private'] | image_access['public'] , necessary for system and cd images)
    @parameter{group_id,list(int)} list of Group ids necessary when access is group, for system and cd images

    @response{list(dict)} list of the images from CM
    """
    # retrieve list of the type requested
    images = IsoImage.objects.exclude(state=image_states['locked'])

    return [img.dict for img in images]


@admin_cm_log(log=True)
def get_by_id(caller_id, iso_image_id):
    """
    @cmview_admin_cm

    @parameter{image_id,int} id of the Image to get
    @parameter{type,image_types} type of image, automatically set, type is in the URL requested

    @response{dict} extended information about specified Image
    """
    return IsoImage.admin_get(iso_image_id).dict


@admin_cm_log(log=True)
def delete(caller_id, iso_image_id):
    """
    Deletes given Image
    @cmview_admin_cm

    @parameter{system_image_id} id of the Image to delete
    @parameter{type,image_types} type of image, automatically set, type is in the URL requested
    """
    image = IsoImage.admin_get(iso_image_id)

    image.check_attached()
    image.state = image_states['locked']
    image.save()


@admin_cm_log(log=True)
def edit(caller_id, iso_image_id, name, description, disk_controller):
    """
    Sets Image's new attributes. Those should be get by src.cm.manager.image.get_by_id().
    @cmview_admin_cm

    @parameter{system_image_id,string} new Image name
    @parameter{name,string} new Image name
    @parameter{description,string} new Image description
    @parameter{disk_controller} new Image controller optional
    @parameter{video_device} new video device optional
    @parameter{network_device} new network device optional
    @parameter{platform} optional
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
    Copy selected image to user's images
    @cmview_admin_cm

    @parameter{src_id,int}
    @parameter{dest_id,int}
    @parameter{img_type}
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
