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

"""@package src.cm.views.user.iso_image
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
@author Maciej Nabożny <mn@mnabozny.pl>
"""

import urllib

from cm.models.iso_image import IsoImage
from cm.models.storage_image import StorageImage
from cm.models.system_image import SystemImage
from cm.models.system_image_group import SystemImageGroup
from cm.models.user import User
from cm.models.vm import VM
from cm.utils import log
from cm.utils.decorators import user_log
from cm.utils.exception import CMException
from cm.utils.threads import image as image_thread
from cm.utils.threads.image import DownloadImage
from common.hardware import disk_controllers, disk_filesystems, network_devices, \
    video_devices
from common.states import image_access, image_states, image_types
import subprocess

@user_log(log=True)
def download(caller_id, name, description, path, disk_controller):
    """
    Downloads specified IsoImage and saves it with specified name and description.

    @cmview_user
    @param_post{name,string}
    @param_post{description,string}
    @param_post{path,string} HTTP or FTP path to IsoImage to download
    @param_post{disk_controller}
    """
    user = User.get(caller_id)

    if not any([path.startswith('http://'), path.startswith('https://'), path.startswith('ftp://')]):
        path = 'http://' + path.strip()

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

    user.check_storage(size / (1024 * 1024))

    image = IsoImage.create(user=user, description=description, name=name, disk_controller=disk_controller, disk_dev=1)

    try:
        image.save()
    except Exception, e:
        log.error(caller_id, "Unable to save image to DB: %s" % str(e))
        raise CMException('image_create')

    DownloadImage(image, path, size).start()


@user_log(log=False)
def get_list(caller_id):
    """
    Returns caller's IsoImages on current CM.

    @cmview_user
    @response{list(dict)} list of the caller's IsoImages on current CM
    """
    # retrieve list of the type requested

    images = IsoImage.objects.exclude(state=image_states['locked']).filter(user__id=caller_id)

    return [img.dict for img in images]


@user_log(log=True)
def get_by_id(caller_id, iso_image_id):
    """
    Returns requested IsoImage provided it belongs to caller.

    @cmview_user
    @param_post{iso_image_id,int} id of the IsoImage to get

    @response{dict} IsoImage.dict property of the requested IsoImage.
    """
    return IsoImage.get(caller_id, iso_image_id).dict


@user_log(log=True)
def delete(caller_id, iso_image_id):
    """
    Deletes specified IsoImage.

    @cmview_user
    @param_post{iso_image_ids} id of the IsoImage to delete
    """
    image = IsoImage.get(caller_id, iso_image_id)

    if image.state != image_states['ok']:
        raise CMException('image_delete')
    try:
        subprocess.call(['rm', image.path])
    except Exception, e:
        raise CMException('image_delete')

    image.check_attached()
    image.state = image_states['locked']
    image.save()


@user_log(log=True)
def edit(caller_id, iso_image_id, name, description, disk_controller):
    """
    Updates IsoImage's attributes.

    @cmview_user
    @param_post{iso_image_id,int} id of the Image to edit
    @param_post{name,string} new name
    @param_post{description,string} new description
    @param_post{disk_controller} new controller (optional)
    """

    image = IsoImage.get(caller_id, iso_image_id)

    if image.state != image_states['ok']:
        raise CMException('image_edit')

    image.name = name
    image.description = description
    image.disk_controller = disk_controller
    try:
        image.save()
    except:
        raise CMException('image_edit')


@user_log(log=True)
def attach(caller_id, iso_image_id, vm_id):
    # vm_id, img_id, destination='usb', check=True/False
    """
    Attaches specified IsoImage to specified VM. It makes possible booting
    any operating system on created VM.

    @cmview_user
    @param_post{iso_image_id,int} id of block device (should be IsoImage type)
    @param_post{vm_id,int} id of the VM which IsoImage should be attached to

    @response{None}
    """

    vm = VM.get(caller_id, vm_id)
    disk = IsoImage.get(caller_id, iso_image_id)

    # Check if disk is already attached to a vm
    if disk.vm:
        raise CMException('image_attached')

    disk.attach(vm)

    try:
        disk.save()
    except:
        raise CMException('iso_image_attach')


@user_log(log=True)
def detach(caller_id, iso_image_id, vm_id):
    """
    Detaches specified IsoImage from specified VM.

    @cmview_user
    @param_post{iso_image_id,int} id of the IsoImage to detach
    @param_post{vm_id,int} id of the VM from which IsoImage should be detached

    @response{None}
    """
    vm = VM.get(caller_id, vm_id)
    disk = IsoImage.get(caller_id, iso_image_id)

    disk.detach(vm)

    try:
        disk.save()
    except:
        raise CMException('iso_image_attach')


@user_log(log=True)
def get_disk_controllers(caller_id):
    """
    @cmview_user
    @response{list(dict)} \c id and \c name of each IsoImage
    """
    return [{'id': id, 'name': name} for name, id in disk_controllers.iteritems()]
