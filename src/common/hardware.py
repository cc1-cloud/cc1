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

"""@package src.common.hardware
Cluster configuration

You can specify here what hardware will be emulated on this cluster and all
supported disk types/formats.  Some variables have python-dictionary format.
Each element is sub-dictionary: <id>: {'param_name': 'param_value', ...}.
Usually required parameters are name and enabled. If any attitional are re-
quired, it is written in comment.
"""

## Network devices available for Virtual Machines. Add own if necessary
#  (virtualizator has to support it!)
network_devices = {
    'rtl8139': 0,
    'virtio': 1,
    'ne2k_pci': 2,
    'e1000': 3
}

## Emulated video devices for Virtual Machines. Add own if necessary
#  (virtualizator has to support it!)
video_devices = {
    'cirrus': 0,
    'vga': 1
}

## Disk controllers for virtual machines.
disk_controllers = {
    'scsi': 0,
    'virtio': 1,
    'ide': 2,
    'sata': 3,
    'usb': 4
}

live_attach_disk_controllers = ['virtio', 'usb']

# Disk filesystems (must be supported by ResourceManager for this CM!)
# Required parameters:
# - name
# - command - formatting program. %%s will be replaced with formatting filename
# - enabled
disk_filesystems = {
    'ntfs': 0,
    'ntfs-full': 1,
    'Fat32': 2,
    'ext2': 3,
    'ext3': 4,
    'ext4': 5,
    'reiserfs': 6,
    'xfs': 7
}

disk_format_commands = {
    'ntfs': '/sbin/mkfs.ntfs -Q -F',
    'ntfs-full': '/sbin/mkfs.ntfs -F',
    'Fat32': '/sbin/mkfs.vfat',
    'ext2': '/sbin/mkfs.ext2 -F',
    'ext3': '/sbin/mkfs.ext3 -F',
    'ext4': '/sbin/mkfs.ext4 -F',
    'reiserfs': '/sbin/mkfs.reiserfs -f -q',
    'xfs': '/sbin/mkfs.xfs -f'
}

video_devices_reversed = dict((v, k) for k, v in video_devices.iteritems())
disk_controllers_reversed = dict((v, k) for k, v in disk_controllers.iteritems())
network_devices_reversed = dict((v, k) for k, v in network_devices.iteritems())
disk_filesystems_reversed = dict((v, k) for k, v in disk_filesystems.iteritems())