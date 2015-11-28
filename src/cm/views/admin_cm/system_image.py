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
def download(caller_id, description, name, path, disk_controller, network_device, platform, video_device):
    """
    Downloads specified SystemImage.

    @cmview_admin_cm
    @param_post{description,string}
    @param_post{name,string}
    @param_post{path,string} HTTP or FTP path to image to download
    @param_post{disk_controller}
    @param_post{network_device}
    @param_post{platform}
    @param_post{video_device}
    """

    # size value is taken
    try:
        connection = urllib.urlopen(path)
        size = int(connection.info()["Content-Length"])
    except IOError:
        log.exception(caller_id, 'Cannot find image')
        raise CMException('image_not_found')
    except KeyError:
        log.exception(caller_id, 'Cannot calculate size')
        raise CMException('image_calculate_size')

    user = User.get(caller_id)

    image = SystemImage.create(name=name, description=description, user=user, platform=platform,
                               disk_controller=disk_controller, network_device=network_device,
                               video_device=video_device)

    try:
        image.save()
    except Exception, e:
        log.error(caller_id, "Unable to save image to DB: %s" % str(e))
        raise CMException('image_create')

    DownloadImage(image, path, size).start()


@admin_cm_log(log=False)
def get_list(caller_id, access, group_id=None):
    """
    Returns images.

    @cmview_admin_cm
    @param_post{access} ( image_access['group'] | image_access['private'] | image_access['public'] , necessary for system and cd images)
    @param_post{group_id,list(int)} list of Group ids necessary when access is group, for system and cd images

    @response{list(dict)} SystemImage.dict property for each SystemImage.
    """
    # retrieve list of the type requested
    images = SystemImage.objects.exclude(state=image_states['locked']).filter(access=access)

    # if group access, we need 'group_id' parameter in 'data'
    # list only images with group access that belong to the group of 'gid' given
    if access == image_access['group']:
        images = images.filter(systemimagegroup__group_id__in=group_id)

    return [img.dict for img in images]


@admin_cm_log(log=True)
def get_by_id(caller_id, system_image_id):
    """
    @cmview_admin_cm
    @param_post{system_image_id,int} id of the Image to get

    @response{dict} extended information about specified Image
    """
    return SystemImage.admin_get(system_image_id).dict


@admin_cm_log(log=True)
def delete(caller_id, system_image_id_list):
    """
    Sets SystemImage state as 'locked'.

    @cmview_admin_cm
    @param_post{system_image_id_list,list(int)} list of the specified Images ids

    @todo Should delete SystemImage and set its state to @val{deleted}.
    """
    for system_image_id in system_image_id_list:
        image = SystemImage.admin_get(system_image_id)
        image.state = image_states['locked']
        image.save()


@admin_cm_log(log=True)
def edit(caller_id, system_image_id, name, description, disk_controller, video_device, network_device, platform):
    """
    Sets Image's new attributes. Those should be get by src.cm.manager.image.get_by_id().

    @cmview_admin_cm
    @param_post{system_image_id,string} new Image name
    @param_post{name,string} new Image name
    @param_post{description,string} new Image description
    @param_post{disk_controller} new Image controller optional
    @param_post{video_device} new video device optional
    @param_post{network_device} new network device optional
    @param_post{platform} optional
    """

    image = SystemImage.admin_get(system_image_id)

    if image.state != image_states['ok']:
        raise CMException('image_edit')

    image.name = name
    image.description = description
    image.disk_controller = disk_controller
    image.video_device = video_device
    image.network_device = network_device
    image.platform = platform
    try:
        image.save()
    except:
        raise CMException('image_edit')


@admin_cm_log(log=True)
def set_private(caller_id, system_image_id):
    """
    Removes SystemImage from public pool.

    @cmview_admin_cm
    @param_post{system_image_id,int}
    """

    image = SystemImage.admin_get(system_image_id)
    image.access = image_access['private']
    # delete the existing group association
    try:
        image.save()
        image.systemimagegroup_set.all().delete()
    except:
        log.exception(caller_id, 'image_set_private')
        raise CMException('image_set_private')


# sets image as group (belonging to group with id group_id)
# only for sys and cd images (from private or public to group)
@admin_cm_log(log=True)
def set_group(caller_id, system_image_id, group_id):
    """
    Method sets specified Image access type as group (belonging to specified Group).

    @cmview_admin_cm
    @param_post{system_image_id,int}
    @param_post{group_id,int} id of the Group Image should belong to

    @response{None}

    @raises{image_set_group,CMException} cannot set group access type
    """
    image = SystemImage.admin_get(system_image_id)
    image.access = image_access['group']

    # create new group-image object
    ig = SystemImageGroup()
    ig.image = image
    ig.group_id = group_id

    try:
        ig.save()
    except:
        raise CMException('image_set_group')


@admin_cm_log(log=True)
def set_public(caller_id, system_image_id):
    """
    Makes SystemImage available in public pool.

    @cmview_admin_cm
    @param_post{system_image_id,int}
    """

    image = SystemImage.admin_get(system_image_id)
    image.access = image_access['public']
    # delete the existing group association
    try:
        image.systemimagegroup_set.all().delete()
        image.save()
    except:
        raise CMException('image_set_public')


@admin_cm_log(log=True)
def convert_to_storage_image(caller_id, system_image_id):
    """
    Changes type of the given Image.

    @cmview_admin_cm
    @param_post{system_image_id,int} ID of an Image to change type of

    @response{None}
    """
    image = SystemImage.admin_get(system_image_id)

    storage_image = StorageImage.create(name=image.name, description=image.description, user=image.user,
                                        disk_controller=image.disk_controller)
    storage_image.state = image_states['ok']
    storage_image.size = image.size

    try:
        storage_image.save()
        os.rename(image.path, storage_image.path)
        image.delete()
    except Exception:
        raise CMException('image_change_type')


@admin_cm_log(log=True)
def get_filesystems(caller_id):
    """
    @cmview_admin_cm
    @response{list(dict)} supported filesystems
    """
    return disk_filesystems


@admin_cm_log(log=True)
def get_video_devices(caller_id):
    """
    @cmview_admin_cm
    @response{list(dict)} video devices
    """
    return video_devices


@admin_cm_log(log=True)
def get_network_devices(caller_id):
    """
    @cmview_admin_cm
    @response{list(dict)} network devices
    """
    return network_devices


@admin_cm_log(log=True)
def get_disk_controllers(caller_id):
    """
    @cmview_admin_cm
    @response{list(dict)} disk controllers
    """
    return disk_controllers


@admin_cm_log(log=True)
def copy(caller_id, src_image_id, dest_user_id):
    """
    Copy selected image to user's images

    @cmview_admin_cm
    @param_post{src_image_id,int}
    @param_post{dest_user_id,int}
    """
    src_image = SystemImage.admin_get(src_image_id)
    dest_user = User.get(dest_user_id)
    dest_image = SystemImage.create(name=src_image.name, description=src_image.description, user=dest_user,
                                    platform=src_image.platform, disk_controller=src_image.disk_controller,
                                    network_device=src_image.network_device, video_device=src_image.video_device)

    try:
        dest_image.save()
    except Exception, e:
        log.error(caller_id, "Unable to commit: %s" % str(e))
        raise CMException('image_create')

    CopyImage(src_image, dest_image).start()
