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

"""@package src.cm.rm.storage_handler
@author Maciej Nabożny <di.dijo@gmail.com>
"""


from cm.utils.exception import CMException
from django.conf import settings
#from rm.utils.decorators import xmllog

import libvirt
from django.template import loader, Context
from django.conf import settings
from cm.utils import log


class StorageHandler:
    """
    Class to mount storages from CM.
    """
    @staticmethod
    #@xmllog
    def mount(info, user_id):
        """
        Mount storage. Info is dict with fields:
            @dictkey{name} name of libvirt pool
            @dictkey{address} storage ip address or hostname
            @dictkey{path} path of remote share on storage
            @dictkey{mountpoint}
            @user_id is the caller, sent for logging
        """
        try:
            settings.configure()
        except:
            pass

        try:
            # Open template file
            template = open("%s/storage.xml" % settings.TEMPLATE_DIR).read()
            # Create django template
            st_template = loader.get_template_from_string(template)
        except Exception, e:
            log.error(user_id, "Error creating template: %s" % str(e))
            raise CMException('storage_create_template')

        try:
            c = Context({'storage': info, 'cc_userid': settings.USER_ID, 'cc_groupid': settings.GROUP_ID})
            t = st_template.render(c)
        except Exception, e:
            log.error(user_id, "Error rendering template: %s" % str(e))
            raise CMException('storage_render_template')

        try:
            conn = libvirt.open('qemu:///system')
        except Exception, e:
            log.debug(user_id, 'Cannot connect to libvirt: %s' % str(e))
            raise CMException('storage_connect_libvirt')

        try:
            pool = conn.storagePoolLookupByName(info['name'])
            log.debug(user_id, "Trying to start existing storage pool...")
            try:
                pool.setAutostart(1)
                pool.build(0)
                pool.create(0)
            except Exception, e:
                log.error(user_id, "Cannot remount defined storage: %s" % str(e))
                raise CMException('storage_not_remounted')
        except:
            try:
                log.debug(user_id, t)
                pool = conn.storagePoolDefineXML(t, 0)
                # TODO: test: 0 - build from scratch; 8 - don't overwerite
                pool.setAutostart(1)
                pool.build(0)
                pool.create(0)
                pool.refresh(0)

                # Create file, which will be used to get path of the storagePool
                f = open("/var/lib/cc1/rm_storages/%s/info" % info['name'], "w")
                f.close()

                pool.refresh(0)
            except Exception, e:
                log.error(user_id, "Cannot create pool: %s" % str(e))
                raise CMException("create_pool")

        #return response('ok')

    @staticmethod
    #@xmllog
    def umount(name):
        """
        Umount filesystem from given storage.
        """
        try:
            conn = libvirt.open('qemu:///system')
        except Exception, e:
            log.debug('Cannot connect to libvirt: %s' % str(e))
            raise CMException('storage_connect_libvirt')

        try:
            pool = conn.storagePoolLookupByName(name)
        except Exception, e:
            log.error("Cannot find storage")
            raise CMException("storage_not_found")

        try:
            pool.destroy()
            pool.undefine()
        except Exception, e:
            log.error("Cannot destroy pool: %s" % str(e))
            raise CMException("storage_destroy")

        #return response('ok')

