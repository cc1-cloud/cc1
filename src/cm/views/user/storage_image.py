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

"""@package src.cm.views.user.storage_image
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
@author Maciej Nabożny <mn@mnabozny.pl>
"""

import urllib

from cm.utils.decorators import user_log
from cm.utils.exception import CMException
from cm.utils import log
from cm.utils.threads.image import DownloadImage, CreateImage
from cm.models.user import User
from cm.models.storage_image import StorageImage
from cm.models.system_image import SystemImage
from cm.models.vm import VM
from common.states import image_states
from common.hardware import disk_controllers, disk_filesystems, network_devices, live_attach_disk_controllers
import os
import subprocess

@user_log(log=True)
def create(caller_id, name, description, filesystem, size, disk_controller):
    """
    Creates new StorageImage.

    @cmview_user
    @param_post{name,string}
    @param_post{description,string}
    @param_post{filesystem,int} id of the filesystem. Supported filesystems are
    common.hardware.disk_filesystems
    @param_post{size,int} size of the SystemImage to create [MB]
    @param_post{disk_controller}

    @response{dict} StorageImage.dict property of newly created StorageImage
    """
    if size < 1:
        raise CMException('image_invalid_size')

    user = User.get(caller_id)
    user.check_storage(size)
    image = StorageImage.create(user=user, disk_controller=disk_controller, description=description, name=name,
                                size=size)

    try:
        image.save()
    except Exception, e:
        log.error(caller_id, "Unable to save image to DB: %s" % str(e))
        raise CMException('image_create')

    CreateImage(image, filesystem).start()
    return image.dict


@user_log(log=True)
def download(caller_id, name, description, path, disk_controller):
    """
    Downloads specified StorageImage.

    @cmview_user
    @param_post{name,string}
    @param_post{description,string}
    @param_post{path,string} HTTP or FTP path to StorageImage to download
    @param_post{disk_controller}
    """
    user = User.get(caller_id)

    if path.startswith('/'):
        size = os.path.getsize(path.strip())
    else:
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

    user.check_storage(size / (1024 * 1024))

    image = StorageImage.create(name=name, description=description, user=user, disk_controller=disk_controller)

    try:
        image.save()
    except Exception, e:
        log.error(caller_id, "Unable to save image to DB: %s" % str(e))
        raise CMException('image_create')

    DownloadImage(image, path, size).start()


@user_log(log=False)
def get_list(caller_id):
    """
    Returns StorageImages.

    @cmview_user
    @response{list(dict)} StorageImage.dict property of each unlocked caller's
    StorageImage
    """
    # retrieve list of the type requested
    images = StorageImage.objects.exclude(state=image_states['locked']).filter(user__id=caller_id)
    return [img.dict for img in images]


@user_log(log=True)
def get_by_id(caller_id, storage_image_id):
    """
    @cmview_user
    @param_post{storage_image_id,int} id of the requested StorageImage

    @response{dict} StorageImage.dict property of the requested StorageImage
    """
    return StorageImage.get(caller_id, storage_image_id).dict


@user_log(log=True)
def delete(caller_id, storage_image_id):
    """
    Deletes given StorageImage from CM storage space. Such an StorageImage
    can in no way be restored. It's also deleted from database.

    @cmview_user
    @param_post{storage_image_ids,list(int)} id of the StorageImage to delete
    """
    image = StorageImage.get(caller_id, storage_image_id)

    if image.state != image_states['ok']:
        raise CMException('image_delete')

    image.check_attached()
    try:
        subprocess.call(['rm', image.path])
    except Exception, e:
        raise CMException('image_delete')

    image.state = image_states['locked']
    image.save()


@user_log(log=True)
def edit(caller_id, storage_image_id, name, description, disk_controller):
    """
    Sets Image's new attributes. Those should be get by src.cm.manager.image.get_by_id().

    @cmview_user
    @param_post{storage_image_id,int} id of the Image to edit
    @param_post{name,string} new Image name
    @param_post{description,string} new Image description
    @param_post{disk_controller} new Image controller optional
    """

    image = StorageImage.get(caller_id, storage_image_id)

    if not image.state in [image_states['ok'], image_states['adding']]:
        raise CMException('image_edit')

    image.name = name
    image.description = description
    image.disk_controller = disk_controller
    try:
        image.save(update_fields=['name', 'description', 'disk_controller'])
    except:
        raise CMException('image_edit')


@user_log(log=True)
def attach(caller_id, storage_image_id, vm_id):
    # vm_id, img_id, destination='usb', check=True/False
    """
    Attaches selected StorageImage to specified VM. Such a disk may be mounted
    to VM so that data generated by VM could be stored on it. VM also has
    access to data already stored on that attached StorageImage.

    @cmview_user
    @param_post{storage_image_id,int} id of a StorageImage block device - Disk Volume Image
    @param_post{vm_id,int} id of the VM which StorageImage should be attached to
    """
    vm = VM.get(caller_id, vm_id)
    disk = StorageImage.get(caller_id, storage_image_id)

    # Check if disk is already attached to a vm
    if disk.vm:
        raise CMException('image_attached')

    disk.attach(vm)

    try:
        disk.save()
    except:
        raise CMException('storage_image_attach')


@user_log(log=True)
def detach(caller_id, storage_image_id, vm_id):
    """
    Detaches specified StorageImage from specified VM.

    @cmview_user
    @param_post{vm_id,int} id of the VM StorageImage should be detached from
    @param_post{storage_image_id,int} id of the StorageImage to detach
    """
    vm = VM.get(caller_id, vm_id)
    disk = StorageImage.get(caller_id, storage_image_id)

    disk.detach(vm)

    try:
        disk.save()
    except:
        raise CMException('storage_image_attach')


@user_log(log=True)
def convert_to_system_image(caller_id, storage_image_id, platform, disk_controller, network_device, video_device):
    """
    Converts StorageImage to SystemImage so that it may be selected as os
    container when creating new VM.

    @cmview_user
    @param_post{storage_image_id,int}
    @param_post{platform}
    @param_post{disk_controller}
    @param_post{network_device}
    @param_post{video_device}
    """
    image = StorageImage.get(caller_id, storage_image_id)
    image.platform = platform
    image.disk_controller = disk_controller
    image.network_device = network_device
    image.video_device = video_device

    try:
        image.recast('cm.systemimage')
        image.save()
    except Exception:
        raise CMException('image_change_type')


@user_log(log=True)
def get_filesystems(caller_id):
    """
    @cmview_user
    @response{list(dict)} common.hardware.disk_filesystems
    """
    return disk_filesystems


@user_log(log=True)
def get_disk_controllers(caller_id):
    """
    @cmview_user
    @response{list(dict)} keys: \c id, \c name, \c live_attach
    """
    return [{'id': id,
          'name': name,
          'live_attach': (name in live_attach_disk_controllers)}
         for name, id in disk_controllers.iteritems()]