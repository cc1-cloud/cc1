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

"""@package src.cm.views.user.system_image
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
@author Maciej Nabożny <mn@mnabozny.pl>
"""

import os
import urllib

from cm.models.iso_image import IsoImage
from cm.models.storage_image import StorageImage
from cm.models.system_image import SystemImage
from cm.models.system_image_group import SystemImageGroup
from cm.models.user import User
from cm.utils import log
from cm.utils.decorators import user_log
from cm.utils.exception import CMException
from cm.utils.threads.image import DownloadImage
from common.hardware import disk_filesystems, disk_controllers, video_devices, \
    network_devices
from common.states import image_access, image_states, image_types
import subprocess

@user_log(log=True)
def download(caller_id, description, name, path, disk_controller, network_device, platform, video_device):
    """
    Downloads image depending on the \c data parameter.
    @cmview_user

    @parameter{path,string} HTTP or FTP path to image to download
    @parameter{name,string}
    @parameter{description,string}

    @parameter{type,image_types} type of image, automatically set, type is in the URL requested

    @response{None}

    @raises{image_not_found,CMException}
    @raises{image_create,CMException}
    """
    user = User.get(caller_id)

    if not any([path.startswith('http://'), path.startswith('https://'), path.startswith('ftp://')]):
        path = 'http://' + path.strip()

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
    user.check_storage(size / (1024 * 1024))

    image = SystemImage.create(name=name, description=description, user=user, platform=platform,
                        disk_controller=disk_controller, network_device=network_device, video_device=video_device)

    try:
        image.save()
    except Exception, e:
        log.error(caller_id, "Unable to save image to DB: %s" % str(e))
        raise CMException('image_create')

    DownloadImage(image, path, size).start()


@user_log(log=True)  # XXX
def get_list(caller_id, access, group_id=None):
    """
    Returns SystemImages with specified access (and from specific Group if
    @prm{group_id} is specified).

    @cmview_user
    @param_post{access} one of common.hardware.image_access
    @param_post{group_id,list(int)} list of Groups ids, required for @val{group} access

    @response{list(dict)} list of the images from CM
    """
    # retrieve list of the type requested
    images = SystemImage.objects.exclude(state=image_states['locked']).filter(access=access)

    # private access
    if access == image_access['private']:
        images = images.filter(user__id__exact=caller_id)

    # if group access, we need 'group_id' parameter in 'data'
    # list only images with group access that belong to the group of 'gid' given
    if access == image_access['group']:
        images = images.filter(systemimagegroup__group_id__in=group_id)

    return [img.dict for img in images]


@user_log(log=True)
def get_by_id(caller_id, system_image_id, groups):
    """
    @cmview_user
    @param_post{groups,list(int)} list of Groups ids, required for @val{group} access
    @param_post{system_image_id,int} id of the requested Image

    @response{dict} SystemImage.dict property of the requested SystemImage
    """
    return SystemImage.get(caller_id, system_image_id, groups).dict


@user_log(log=True)
def delete(caller_id, system_image_id):
    """
    Deletes specified SystemImage

    @cmview_user
    @param_post{system_image_ids,list(int)} id of the SystemImage to delete
    """
    image = SystemImage.get(caller_id, system_image_id)

    if image.state != image_states['ok']:
        raise CMException('image_delete')

    try:
        subprocess.call(['rm', image.path])
    except Exception, e:
        raise CMException('image_delete')

    image.state = image_states['locked']
    image.save()


@user_log(log=True)
def edit(caller_id, system_image_id, name, description, disk_controller, video_device, network_device, platform):
    """
    Updates attributes of the specified SystemImage.

    @cmview_user
    @param_post{system_image_id,int} id of the SystemImage to edit
    @param_post{name,string} SystemImage new name (optional)
    @param_post{description,string} SystemImage new description (optional)
    @param_post{disk_controller} SystemImage new controller (optional)
    @param_post{video_device} SystemImage new video device (optional)
    @param_post{network_device} SystemImage new network device (optional)
    @param_post{platform} (optional)
    """

    image = SystemImage.get(caller_id, system_image_id)

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


@user_log(log=True)
def set_private(caller_id, system_image_id, leader_groups):
    """
    Marks SystemImage as @val{private}. The caller needs to be:
    - either the <b>owner of the SystemImage</b>
    - or the <b>leader of the group</b> to which SystemImage belongs

    @cmview_user
    @param_post{system_image_id,int} id of the Image to set private
    @param_post{leader_groups,list(int)} ids of the group where the caller is
    leader, requierd if Image's access type is group
    """

    image = SystemImage.get(caller_id, system_image_id, leader_groups)
    image.access = image_access['private']
    # delete the existing group association
    try:
        image.save()
        image.systemimagegroup_set.all().delete()
    except:
        log.exception(caller_id, 'image_set_private')
        raise CMException('image_set_private')


@user_log(log=True)
def set_group(caller_id, system_image_id, group_id):
    """
    Method sets specified Image access type as group (belonging to specified Group)
    (only for sys and cd images - from private or public to group)

    @cmview_user
    @param_post{group_id,int} id of the Group Image should belong to
    @param_post{system_image_id,int}

    @response{None}
    """
    image = SystemImage.get(caller_id, system_image_id)
    image.access = image_access['group']

    # create new group-image object
    ig = SystemImageGroup()
    ig.image = image
    ig.group_id = group_id

    try:
        ig.save()
        image.save()
    except:
        raise CMException('image_set_group')


@user_log(log=True)
def convert_to_storage_image(caller_id, system_image_id):
    """
    Changes type of the given Image.

    @cmview_user
    @param_post{system_image_id,int} ID of an Image to change type of
    """
    image = SystemImage.get(caller_id, system_image_id)
    try:
        image.recast('cm.storageimage')
        image.save()
    except Exception:
        log.exception(caller_id, "convert_to_storage_image")
        raise CMException('image_change_type')


@user_log(log=True)
def get_filesystems(caller_id):
    """
    @cmview_user
    @response{list(dict)} common.hardware.disk_filesystems
    """
    return disk_filesystems


@user_log(log=True)
def get_video_devices(caller_id):
    """
    @cmview_user
    @response{list(dict)} common.hardware.video_devices
    """
    return video_devices


@user_log(log=True)
def get_network_devices(caller_id):
    """
    @cmview_user
    @response{list(dict)} common.hardware.network_devices
    """
    return network_devices


@user_log(log=True)
def get_disk_controllers(caller_id):
    """
    @cmview_user
    @response{list(dict)} \c id and \c name for each disk controller
    """
    return [{'id': id, 'name': name} for name, id in disk_controllers.iteritems()]
