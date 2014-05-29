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

"""@package src.cm.utils.threads.image
"""
import subprocess

import threading
import urllib2
from common.states import image_states
from common.hardware import disk_format_commands, disk_filesystems_reversed
import os
from cm.utils import log
import random
import hashlib

class CreateImage(threading.Thread):
    image = None
    filesystem = None
    def __init__(self, image, filesystem):
        threading.Thread.__init__(self)
        self.image = image
        self.filesystem = filesystem

    def run(self):
        if os.path.exists(self.image.path):
            self.image.state = image_states['failed']
            self.image.save(update_fields=['state'])
            log.error(self.image.user.id, "Destination image %d for user %d exists! Aborting creation" % (self.image.id, self.image.user.id))
            return
        self.image.progress = 0

        if self.format() == 'failed':
            self.image.state = image_states['failed']
        # file = open(self.image.path, 'w')
        # file.seek(self.image.size)
        # file.write(' ')
        # file.close()
        #
        # self.image.progress = 75
        # self.image.save()
        # # TODO: Format image by self.format
        #
            self.image.save(update_fields=['state'])
        else:
            self.image.progress = 100
            self.image.state = image_states['ok']
            self.image.save(update_fields=['state', 'progress'])

        log.debug(self.image.user.id, 'stage [6/6] cleaning..')
        try:
            os.remove('%s' % os.path.join('/var/lib/cc1/images-tmp/', os.path.split(self.image.path)[1]))
        except Exception, e:
            log.error(self.image.user.id, 'error remove file: %s' % str(e))

    def exec_cmd(self, args):
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retr_std = p.stdout.read()
        ret = p.wait()
        if ret:
            retr_err = str(p.stderr.read())
            log.error(self.image.user.id, retr_err)
            log.error(self.image.user.id, retr_std)
            return retr_err

    def set_progress(self, prg):
        self.image.progress = prg
        self.image.save(update_fields=['progress'])

    def format(self):

        if not os.path.exists(os.path.dirname(self.image.path)):
            os.makedirs(os.path.dirname(self.image.path))

        if not os.path.exists(os.path.dirname('/var/lib/cc1/images-tmp/')):
            os.makedirs(os.path.dirname('/var/lib/cc1/images-tmp/'))

        tmp_path = os.path.join('/var/lib/cc1/images-tmp/', os.path.split(self.image.path)[1])

        log.debug(self.image.user.id, 'stage [1/6] truncate partition file')
        if self.exec_cmd(['truncate', '-s', '%dM' % self.image.size, '%s' % tmp_path]):
            return 'failed'
        self.set_progress(random.randint(0,15))

        format_cmd = disk_format_commands[disk_filesystems_reversed[self.filesystem]].split()
        format_cmd.append('%s' % tmp_path)
        log.debug(self.image.user.id, 'stage [2/6] creating partition filesystem')
        if self.exec_cmd(format_cmd):
            return 'failed'
        self.set_progress(random.randint(15,50))

        log.debug(self.image.user.id, 'stage [3/6] creating disk')
        if self.exec_cmd(['/usr/bin/ddrescue', '-S', '-o', '1048576', '%s' % tmp_path, str(self.image.path)]):
            return 'failed'
        self.set_progress(random.randint(50,80))

        log.debug(self.image.user.id, 'stage [4/6] creating new partition table')
        if self.exec_cmd(['/sbin/parted', '-s', str(self.image.path), 'mklabel', 'msdos']):
            return 'failed'
        self.set_progress(random.randint(80,90))

        log.debug(self.image.user.id, 'stage [5/6] adding partition')
        if self.exec_cmd(['/sbin/parted', '-s', str(self.image.path), 'mkpart', 'primary', '1048576b', '100%']):
            return 'failed'
        self.set_progress(random.randint(90,100))


        log.info(self.image.user.id, 'disk succesfully formatted')

class DownloadImage(threading.Thread):
    image = None
    url = None
    size = 0
    def __init__(self, image, url, size):
        threading.Thread.__init__(self)
        self.image = image
        self.url = url
        self.size = size

    def run(self):
        try:
            if self.url.startswith('/'):
                src_image = open(self.url, 'r')
            else:
                src_image = urllib2.urlopen(self.url)
        except Exception, e:
            log.exception(self.image.user.id, "Cannot open url %s: %s" % (self.url, str(e)))
            self.image.state = image_states['failed']
            return

        if os.path.exists(self.image.path):
            self.image.state = image_states['failed']
            self.image.save(update_fields=['state'])
            log.error(self.image.user.id, "Destination image %d for user %d exists! Aborting download" % (self.image.id, self.image.user.id))
            return

        try:
            dirpath = os.path.dirname(self.image.path)
            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
            dest_image = open(self.image.path, 'w')
            downloaded_size = 0
            md5sum = hashlib.md5()
            while downloaded_size < self.size:
                buffer = src_image.read(1024*1024)
                md5sum.update(buffer)
                downloaded_size += len(buffer)
                dest_image.write(buffer)

                progress = int(downloaded_size * 100 / self.size)
                if progress != self.image.progress:
                    self.image.progress = progress
                    self.image.save(update_fields=['progress'])

            dest_image.close()

            log.info(self.image.user.id, "md5 hash of image %d is %s" % (self.image.id, md5sum.hexdigest()))
            self.image.state = image_states['ok']
            self.image.size = downloaded_size / (1024*1024)
            self.image.save(update_fields=['progress', 'state', 'size'])
            message.info(self.image.user.id, 'image_downloaded', {'name': self.image.name, 'md5sum': md5sum.hexdigest()})
        except Exception, e:
            log.exception(self.image.user.id, "Failed to download image: %s" % str(e))
            self.image.state = image_states['failed']
            self.image.save(update_fields=['state'])


class CopyImage(threading.Thread):
    def __init__(self, src_image, dest_image):
        threading.Thread.__init__(self)
        self.src_image = src_image
        self.dest_image = dest_image

    def run(self):
        copied = 0
        prev_progress = 0
        try:
            size = os.path.getsize(self.src_image.path)
            dirpath = os.path.dirname(self.dest_image.path)
            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
            src = open(self.src_image.path, "r")
            dst = open(self.dest_image.path, "w")
            while 1:
                buff = src.read(1024 * 1024)  # Should be less than MTU?
                if len(buff) > 0 and copied <= size:
                    dst.write(buff)
                    copied = copied + len(buff)
                else:
                    break
                # Update image information:
                progress = 100 * copied / size
                if progress > prev_progress:
                    prev_progress = progress
                    self.dest_image.progress = progress
                    self.dest_image.save(update_fields=['progress'])

            self.dest_image.state = image_states['ok']
            self.dest_image.size = self.src_image.size
            self.dest_image.save(update_fields=['progress', 'state', 'size'])

            src.close()
            dst.close()
        except Exception, e:
            log.exception(self.dest_image.user.id, "Failed to copy image: %s" % str(e))
            self.dest_image.state = image_states['failed']
            self.dest_image.save(update_fields=['state'])
