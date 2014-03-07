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
"""@package src.cm.rm.image_handler

@author Maciej Nabożny <di.dijo@gmail.com>
"""

import subprocess
import os
import time
import libvirt
import urllib
import hashlib
import threading
# from multiprocessing import Process


from common.states import image_states, image_types
from cm.utils.exception import CMException
from cm.utils import log
from cm.utils.functions import execute
"""
from rm.utils.decorators import xmllog
from rm.utils.rmi import rmi
from common import response
from rm.utils import log
"""

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO:new implementation with multiprocessing
# implement functions as SubProcess instead of threads
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class ImageHandler:
    """
    Manage disks in CM/LM
    """
    @staticmethod
    # @xmllog
    def create(data):
        """
        Create new, empty image.

        @parameter{data,dict}
        \n fields:
        @dictkey{dest_pool} destination pool name
        @dictkey{dest_userid} destination user id
        @dictkey{size} size of image in MB
        @dictkey{id} image id (will be returned to lm.image.finished, progress or failed)
        @dictkey{format_command} (optional) mkfs command
        """

        # rmi().image.rmi.update(data['user_id'], {'image_id': data['id'], 'state': image_states['adding'], 'progress': 0})
        ImageUtils.update(data['user_id'], {'image_id': data['id'], 'state': image_states['adding'], 'progress': 0, 'type':data['type']})
        # t = ImageSubprocess('create', data)
        # t.start()
        t = ImageThread("create_thread", 'create', data)
        t.start()
        
        # return response('ok')
    
    @staticmethod
    # @xmllog
    def copy(data):
        """
        Create new, empty image.
        
        @parameter{data,dict}
        \n fields:
        @dictkey{user_id} who is calling?
        @dictkey{src_pool} source pool name
        @dictkey{src_userid} source user_id
        @dictkey{src_imgid} source image id
        @dictkey{dest_pool} destination pool name
        @dictkey{dest_userid} destination user id
        @dictkey{dest_imageid} destination image id
        """
        # t = ImageSubprocess('copy', data)
        # t.start()
        t = ImageThread("copy_thread", 'copy', data)
        t.start()
        
        # return response('ok')
    
    @staticmethod
    # #@xmllog
    def download(data):
        """
        Download image from link or path.
        
        @parameter{data,dict}
        \n fields: 
        @dictkey{dest_pool} destination pool name
        @dictkey{dest_userid} destination user id
        @dictkey{source} url to image
        @dictkey{id} image id (will be returned to lm.image.finished, progress or failed)
        @dictkey{size} maximum image size in MB
        """
        # rmi().image.rmi.update(data['user_id'], {'image_id': data['id'], 'state': image_states['adding'], 'progress': 0})
        ImageUtils.update(data['user_id'], {'image_id': data['id'], 'state': image_states['adding'], 'progress': 0, 'type':data['type']})
        # t = ImageSubprocess('download', data)
        # t.start()
        t = ImageThread("download_thread", 'download', data)
        t.start()
        
        # return response('ok')
    
    @staticmethod
    # @xmllog
    def delete(data):
        """
        Delete image from storage.
        
        @parameter{data,dict}
        \n fields:
        @dictkey{dest_pool} destination pool name
        @dictkey{dest_userid} destination user id
        @dictkey{id} image id (will be returned to lm.image.finished, progress or failed)
        """
        try:
            path = ImageUtils.get_path(data)
            image_id = data['id']
        except:
            log.debug(data['dest_userid'], "incomplete_information")
            ImageUtils.failed(data['user_id'], {'image_id':image_id, 'status': 'incomplete_information', 'type':data['type']})
            # rmi().image.rmi.failed(image_id, {'status': 'incomplete_information'})
            return
            
        subprocess.call(['rm', path])
        # return response('ok')
        # rmi().image.rmi.finished(image_id)
        



# class which define a new thread for image operation
class ImageThread (threading.Thread):
    def __init__(self, name, action, data):
        threading.Thread.__init__(self)
        # self.threadID = threadID
        self.name = name
        self.action = action
        self.data = data

    def run(self):
        """
        @todo new implementation with multiprocessing
        p = Process(target=getattr(self, self.action))
        p.daemon = True
        p.start()
        p.join()
        """
        log.debug(self.data['user_id'], "Executing thread image operation: %s" % self.name)
        log.debug(self.data['user_id'], "Args: %s" % self.data)
        # execute the function
        getattr(self, self.action)()
        log.debug(self.data['user_id'], "Executed thread image operation: %s" % self.name)

    # @xmllog
    def create(self):
        """
        Create new image. self.data should same as in ImageHandler.create
        """
        try:
            destination = ImageUtils.get_path(self.data)
            size = self.data['size']
            image_id = self.data['id']
            user_id = int(self.data['user_id'])
            image_type = self.data['type']
            log.debug(user_id, destination)
        except:
            # rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'image_create_incomplete_information'})
            ImageUtils.failed(user_id, {'image_id': image_id, 'status': 'image_create_incomplete_information', 'type':self.data['type']})
            return
            # sys.exit(1)
        
        if size < 2:
            # rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'image_too_small'})
            ImageUtils.failed(user_id, {'image_id': image_id, 'status': 'image_too_small', 'type':self.data['type']})
            return
            # sys.exit(1)

        # subprocess.call execute new process with command given
        subprocess.call(['mkdir', '-p', '%s' % os.path.dirname(destination)])
        subprocess.call(['chmod', '700', os.path.dirname(destination)])
        # TODO: Move 331 uid and gid to config
        subprocess.call(['chown', '331', os.path.dirname(destination)])
        subprocess.call(['chgrp', '331', os.path.dirname(destination)])

        
        # dd command copy data blocks from 'if' to 'of'
        r = execute(['dd', 'if=/dev/zero', 'of=%s' % destination, 'bs=1M', 'count=1', 'seek=%d' % (int(size) - 1)])
        
        if r != 0:
            # rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'dd_failed'})
            ImageUtils.failed(user_id, {'image_id': image_id, 'status': 'dd_failed', 'type':image_type})
            # log.error(user_id ,"image_dd_failed")
            return
            # sys.exit(1)
        
           
        log.debug(user_id , "chmod")
        subprocess.call(['chmod', '600', destination])
        
        # TODO: Move 331 uid/gid to config
        log.debug(user_id , "chown")
        subprocess.call(['chown', '331', destination])
        log.debug(user_id , "chgrp")
        subprocess.call(['chgrp', '331', destination])
        
        # Format image
        if 'format_command' in self.data:
            # rmi().image.rmi.update(user_id, {'image_id': image_id, 'state': image_states['formatting'], 'progress': 0})
            ImageUtils.update(user_id, {'image_id': image_id, 'state': image_states['formatting'], 'progress': 0, 'type':image_type})
            try:
                ImageUtils.format(self.data)
            except Exception, e:
                # log.error(user_id ,"Formatting image: %s" % str(e))
                # rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'format_failed'})
                ImageUtils.failed(user_id, {'image_id': image_id, 'status': 'format_failed', 'type':image_type})
                return
                # sys.exit(1)
        
        log.debug(user_id , "return size")
        filesize = os.path.getsize(destination) / 1024 / 1024
        
        ImageUtils.created(user_id, {'image_id': image_id, 'size': filesize, 'type':image_type})
        # rmi().image.rmi.created(user_id, {'image_id': image_id, 'size': filesize})
        
        # sys.exit(0)
    
    # @xmllog
    def copy(self):
        """
        Copy image to another user
        """
        try:
            user_id = self.data['user_id']
            dest_imageid = self.data['dest_imageid']
            dest_pool = self.data['dest_pool']
            dest_userid = self.data['dest_userid']
            image_type = self.data['type']
            src_pool = self.data['src_pool']
            src_userid = self.data['src_userid']
            src_imgid = self.data['src_imgid']
        except Exception, e:
            # rmi().image.rmi.failed(user_id, {'image_id': dest_imageid, 'status': 'imiage_incomplete_information'})
            ImageUtils.failed(user_id, {'image_id': dest_imageid, 'status': 'image_incomplete_information', 'type':image_type})
            # log.error(user_id ,"image_incomplete_information")
            return
            # sys.exit(1)
        
        try:
            
            # directory must first be created, to create file to write
            destination = ImageUtils.get_path({'dest_pool': dest_pool, 'dest_userid': dest_userid, 'id': dest_imageid, 'type':image_type})
            
            # subprocess.call execute new process with command given
            subprocess.call(['mkdir', '-p', '%s' % os.path.dirname(destination)])
            subprocess.call(['chmod', '700', os.path.dirname(destination)])
            # TODO: Move 331 uid and gid to config
            subprocess.call(['chown', '331', os.path.dirname(destination)])
            subprocess.call(['chgrp', '331', os.path.dirname(destination)])
            
            src = open(ImageUtils.get_path({'dest_pool': src_pool, 'dest_userid': src_userid, 'id': src_imgid, 'type':image_type}), "r")
            dst = open(destination, "w+")
        except Exception, e:
            ImageUtils.failed(user_id, {'image_id': dest_imageid, 'status': 'image_not_found', 'type':image_type})
            # #mi().image.rmi.failed(user_id, {'image_id': dest_imageid, 'status': 'image_not_found'})
            # log.error(user_id ,"image_not_found")
            return 
            # sys.exit(1)
        
        
            
        copied = 0
        size = os.path.getsize(ImageUtils.get_path({'dest_pool': src_pool, 'dest_userid': src_userid, 'id': src_imgid, 'type':image_type}))
        size /= 1048576
        while 1:
            buff = src.read(1024 * 1024)  # Should be less than MTU?
            if len(buff) > 0 and copied <= size:
                dst.write(buff)
                copied = copied + len(buff) / 1048576
            else:
                break
            # Update image information:
            if (100 * copied / size) % 5 == 0:
                ImageUtils.update(self.data['user_id'], {'image_id': dest_imageid, 'state': image_states['adding'], 'progress': (100 * copied) / size, 'type':image_type})
                # #rmi().image.rmi.update(self.data['user_id'], {'image_id': dest_imageid, 'state': image_states['adding'], 'progress': (100*copied/size)})
        
        dst.close()

        # destination = ImageUtils.get_path({'dest_pool': dest_pool, 'dest_userid': dest_userid, 'id': dest_imageid,'type':type})
        filesize = os.path.getsize(destination) / 1024 / 1024
        subprocess.call(['chmod', '600', destination])
        
        # TODO: Move 331 uid/gid to config
        subprocess.call(['chown', '331', destination])
        subprocess.call(['chgrp', '331', destination])
        
        ImageUtils.created(user_id, {'image_id': dest_imageid, 'size': filesize, 'type':image_type})
        # #rmi().image.rmi.created(user_id, {'image_id': dest_imageid, 'size': filesize})
        
        # log.debug(user_id,"exit")
        # sys.exit(0)
        
        
        
    # @xmllog
    def download(self):
        """
        Create new image. self.data should same as in ImageHandler.create
        """
        try:
            user_id = self.data['user_id']
            image_id = self.data['id']
            image_type = self.data['type']
            source = self.data['source']
            destination = ImageUtils.get_path(self.data)
            size = self.data.get('size') or None
            # if size == 0:
            #    #rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'image_size'})
            #    exit(0)
        except Exception, e:
            
            # rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'image_incomplete_information'})
            ImageUtils.failed(user_id, {'image_id': image_id, 'status': 'image_incomplete_information', 'type':image_type})
            # log.error(user_id ,"image_incomplete_information")
            return
            # sys.exit(1)
        
        subprocess.call(['mkdir', os.path.dirname(destination)])
        subprocess.call(['chmod', '700', os.path.dirname(destination)])
        # TODO: Move 331 uid/gid to config
        subprocess.call(['chown', '331', os.path.dirname(destination)])
        subprocess.call(['chgrp', '331', os.path.dirname(destination)])
        
        try:
            dst = open(destination, "w")
        except Exception, e:
            ImageUtils.failed(user_id, {'image_id': image_id, 'status': 'image_not_found', 'type':image_type})
            log.error(user_id, "Cannot open image: %s" % str(e))
            # rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'image_not_found'})
            return
            # sys.exit(1)
        
        
        # Calculate size
        size = None
        try:
            src = urllib.urlopen(source)
            size = int(src.info()["Content-Length"])
        except Exception:
            if os.path.exists(source):
                size = os.path.getsize(source)
            else:
                log.exception(user_id, 'Cannot calculate size')
                # rmi().image.rmi.failed(user_id, {'image_id': image_id, 'status': 'image_not_found'})
                ImageUtils.failed(user_id, {'image_id': image_id, 'status': 'image_not_found', 'type':image_type})
                raise CMException('image_calculate_size')
        
        
        downloaded = 0
        step = int(size / 50)
        if step == 0:
            step = 1
        while 1:
            buff = src.read(1024 * 1024)  # Should be less than MTU?
            if len(buff) > 0 and (size == None or downloaded <= size):
                dst.write(buff)
                downloaded = downloaded + len(buff)
            else:
                break
            # Update image information:
            if size != None and (int(float(downloaded) / float(size)) * 100) % step == 0:
                ImageUtils.update(self.data['user_id'], {'image_id': image_id, 'state': image_states['adding'], 'progress': (100 * downloaded / size), 'type':image_type})
                # rmi().image.rmi.update(self.data['user_id'], {'image_id': image_id, 'state': image_states['adding'], 'progress': (100 * downloaded / size)})
        

        dst.close()
        filesize = os.path.getsize(destination) / 1024 / 1024
        subprocess.call(['chmod', '600', destination])
        
        # TODO: Move 331 uid/gid to config
        subprocess.call(['chown', '331', destination])
        subprocess.call(['chgrp', '331', destination])
        
        md5sum = ImageUtils.md5sum(self.data)
        log.debug(user_id, "md5: %s" % md5sum)
        ImageUtils.downloaded(user_id, {'image_id': image_id, 'size': filesize, 'md5sum': md5sum, 'type':image_type})
        # rmi().image.rmi.downloaded(user_id, {'image_id': image_id, 'size': filesize, 'md5sum': md5sum})
        
        # log.debug(user_id, "exit")
        # sys.exit(0)
        
class ImageUtils:
    """
    Additional functions for disk management
    """
    
    @staticmethod
    # #@xmllog
    def get_path(data):
        """
        Create path from given LV pool name, user id, type of image and image id. 
        
        Data should be a dictionary with fields:
            @dictkey{dest_pool} destination pool name
            @dictkey{dest_userid} user id
            @dictkey{id} image id
            @dictkey{type} image type
        """
        # TODO: log gives problem
        # log.debug(data['dest_userid'],data)
        try:
            pool_name = data['dest_pool']
            user_id = int(data['dest_userid'])
            image_id = int(data['id'])
            image_type = data['type']
        except:
            log.error(user_id, 'Incomplete information in get_path')
            raise CMException('image_getpath_incomplete_information')
        
        try:
            conn = libvirt.open('qemu:///system')
        except Exception, e:
            log.debug(user_id, 'Cannot connect to libvirt: %s' % str(e))
            raise CMException('storage_connect_libvirt')
        
        try:
            pool = conn.storagePoolLookupByName(pool_name)
            usr_dir = "%s/%d" % (os.path.dirname(pool.storageVolLookupByName("info").path()), user_id)
        except Exception, e:
            log.error(user_id, "Cannot get libvirt pool: %s" % str(e))
            raise CMException('rm_pool')
        
        
        # check type image to add it to the img path
        if image_type == image_types['cd']:
            type_str = "ISO"
        elif image_type == image_types['vm']:
            type_str = "SYS"
        elif image_type == image_types['storage']:
            type_str = "STG"
        else:
            log.error(user_id, "image_unsupported")
            raise CMException('image_unsupported')
        
        # between usr_dir and image_id we put the TYPE of image
        # usr_dir/type/image_id
        # e.g.: /home/gaet/rm_storages/storage1/1/DISKVOL_23
        
        return "%s/%s_%s" % (usr_dir, type_str, image_id)
        # return "%s/%s" % (usr_dir,image_id)
    
    
    @staticmethod
    # #@xmllog
    def format(data):
        """
        Make partition table and format file with given filesystem.
        
        Data should be a dictionary with fields:
        @dictkey{path}
        @dictkey{format_command} commamd to format
        @dictkey{format_args} command arguments. %s will be replaced with file path
        """
        try:
            path = ImageUtils.get_path(data)
            format_command = data['format_command']
        except:
            raise CMException('incomplete_information')
        
        log.info(data['user_id'], 'Creating filesystem on %s by command: %s' % (path, format_command % path))
        log.debug(data['user_id'], "Looking for unused loopback")
        p = subprocess.Popen(['losetup', '-f'], stdout=subprocess.PIPE)
        loopname = str(p.stdout.read())[:-1]
        log.debug(data['user_id'], "\t Unused loopback: %s" % loopname)
        p.wait()
        
        try:
            log.debug(data['user_id'], "Mounting loopback: %s -> %s" % (loopname, path))
            p = subprocess.Popen(['losetup', loopname, path])
            p.wait()
        
        
            log.debug(data['user_id'], "Creating partition table on " + loopname + "...")
            p = subprocess.Popen(['parted', '-s', loopname, 'mktable', 'msdos'], stdin=subprocess.PIPE)
            p.wait()
            
            log.debug(data['user_id'], "Creating partition on " + loopname + "...")
            p = subprocess.Popen(['parted', '-s', loopname, 'mkpart', 'primary', '0%', '100%'], stdin=subprocess.PIPE)
            p.wait()
            
            log.debug(data['user_id'], "Mapping loopback with kpartx...")
            p = subprocess.Popen(['kpartx', '-a', loopname])
            p.wait()
            
            # TODO: split format_command string to list by inteligent function.
            # First element of splitted format_command should be a mkfs binary
            if os.path.exists(format_command.split()[0]):
                partition = '/dev/mapper/%sp1' % loopname.split('/')[2]
                log.debug(data['user_id'], "Formating %s" % partition)
                command = format_command % partition
                p = subprocess.Popen(command, shell=True)
                p.wait()
            else:
                raise CMException('rm_format_command')
            
            log.debug(data['user_id'], "Cleaning the balagan...")
            p = subprocess.Popen(['kpartx', '-d', loopname])
            p.wait()
            p = subprocess.Popen(['losetup', '-d', loopname])
            p.wait()
        except Exception, e:
            log.error(data['user_id'], "Cleaning after disaster: %s" % str(e))
            # Try to umount kpartx. If nfs was unavailable while
            # formating, then kernel hangs every process which
            # try to access file loopX, mapper/partX etc. We
            # don't want to wait for this processes. RM restart
            # is required then
            try:
                p = subprocess.Popen(['kpartx', '-d', loopname])
                # p.wait()
            except Exception:
                log.exception(data['user_id'], "Cannot delete device mapper")
            
            time.sleep(5)
            
            try:
                p = subprocess.Popen(['losetup', '-d', loopname])
                # p.wait()
            except Exception:
                log.exception(data['user_id'], "Cannot delete loopback")
            time.sleep(5)
            raise CMException('format_failure')
        
        # return response('ok')
        
        
    
    @staticmethod
    # @xmllog
    def md5sum(data):
        fp = open(ImageUtils.get_path(data))
        m = hashlib.md5()
        while True:
            d = fp.read(8096)
            if not d:
                break
            m.update(d)
        return m.hexdigest()

    @staticmethod
    def created(user_id, data):
        """
        Image created
        """
        
        """
        #check if information have been sent, not necessary now
        try:
            image_id = data['image_id']
        except Exception, e:
            log.error(user_id, "Failed to finish image operation. Incomplete data dictionary: %s" % str(e))
            return response('image_params')
        """
        try:
            # use admin_get caues no need to check permissions here
            image = image_utils.admin_get(data['image_id'], data['type'])
            # TODO: created should be only for disk volumes, is type necessary? 
            # image = StorageImage.objects.get(pk=data['image_id'])
            # image = Session.query(Image).get(image_id)
        except Exception, e:
            log.error(user_id, "Cannot get image: %s" % str(e))
            # return response('image_no_image')
            
        try:
            image.state = image_states['ok']
            image.size = data['size']
            image.save()
            # Session.commit()
        except Exception, e:
            log.error(user_id, "Cannot update image: %s" % str(e))
            # Session.rollback()
        
        log.debug(user_id, "Image finished")
        # TODO: send message to CLM
        # message.info(user_id, 'image_created', {'name': image.name})
        # return response('ok')
    
    @staticmethod
    def downloaded(user_id, data):
        """
        Downloads Image.
        @parameter{user_id,int}
        @parameter{data,dict}, \n fields:
        @dictkey{image_id}
        @dictkey{size,int} declared size of the Image [MB]
        @dictkey{md5sum}
        @resonse{none}
        """
        try:
            image = image_utils.get(user_id, data['image_id'], data['type'])
            # image = Session.query(Image).get(image_id)
        except Exception, e:
            log.error(user_id, "Cannot get image: %s" % str(e))
            # return response('image_no_image')
            
        try:
            image.state = image_states['ok']
            image.size = data['size']
            image.save()
            # Session.commit()
        except Exception, e:
            log.error(user_id, "Cannot update image: %s" % str(e))
            # Session.rollback()
        
        log.debug(user_id, "Image finished")
        # TODO: send message to CLM
        # message.info(user_id, 'image_downloaded', {'name': image.name, 'md5sum': data['md5sum']})
        # return response('ok')
        
    @staticmethod
    def failed(user_id, data):
        """
        Marks image as failed.
        """
        try:
            image = image_utils.get(user_id, data['image_id'], data['type'])
            # image = Session.query(Image).get(image_id)
        except Exception, e:
            log.error(user_id, "Cannot update image. Image %d not found: %s" % (data['image_id'], str(e)))
            # return response('image_no_image')
        
        try:
            image.state = image_states['failed']
            image.save()
            # Session.commit()
        except Exception, e:
            log.error(user_id, "Cannot update image: %s" % str(e))
            # return response('image_status_update')
            # Session.rollback()
        
        log.error(user_id, "Image failed: %s" % data['status'])
        # TODO: Message
        # return response('ok')
    
    @staticmethod
    def update(user_id, data):
        """
        Updates image as described by data.
        
        @parameter{user_id,int}
        @parameter{data,dict}
        \n fields:
        @dictkey{image_id,int} id of image to update
        - state
        - progress
        """
        log.debug(user_id, data)
        
        image_id = data['image_id']
        state = data['state']
        image_type = data['type']
        progress = data['progress']

            
        try:
            # admin_get cause no need to check permissions here
            image = image_utils.admin_get(image_id, image_type)
            # image = Session.query(Image).get(image_id)
        except Exception, e:
            log.error(user_id, "Cannot update image. Image %d not found: %s" % (image_id, str(e)))
            # return response('image_no_image')
        
        try:
            image.state = state
            image.progress = progress
            image.save()
            # Session.commit()
        except Exception, e:
            log.error(user_id, "Cannot update image: %s" % str(e))
            # return response('image_status_update')
            # Session.rollback()
        # return response('ok')
