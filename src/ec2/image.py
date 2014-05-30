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
from M2Crypto import RSA, EVP
from binascii import unhexlify
import os
import tarfile
import uuid
from xml.dom import minidom
import thread
from common.hardware import disk_controllers, network_devices, video_devices
from common.states import image_access, image_types, image_states, group_states
from ec2.base.action import Action, CLMException
from ec2.error import InvalidAMIID, MissingParameter, InternalError, \
    UndefinedError, InvalidParameterValue, InvalidFilter, InvalidManifest, InvalidParameter
from ec2.helpers.entities import Entity
from ec2.helpers.filters import applyEc2Filters, validateEc2Filters
from ec2.helpers.parse import parseFilters, parseID, parseIDs
from ec2.settings import BUCKETS_PATH
from ec2.settings import EC2_PRIVATE_KEY, EC2_CM_INTERFACE
from ec2.settings import UPLOAD_IMAGES_PATH

"""@package src.ec2.image
EC2 actions for images

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Rafał Grzymkowski
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Miłosz Zdybał
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


# Use windows if you have Windows based AMIs; otherwise leave blank.
# Type: String
# Valid Value: windows
PLATFORM = {
    0: '',           # unknown
    1: '',           # linux
    2: '',           # unix
    3: 'windows',    # windows
    4: '',           # mac os
    5: '',           # other
}

# State of the image.
# Type: String
# Valid Values: available | pending | failed
STATE = {
    0: 'available',  # ok
    1: 'failed',     # locked
    2: 'pending',    # adding
    3: 'failed',     # failed
    4: 'failed',     # unavailable
}

IMAGE_READ_BUFFER = 65536

class DeregisterImage(Action):
    def _execute(self):
        try:
            image_id = parseID(self.parameters['ImageId'], Entity.image)
            if not image_id:
                raise InvalidParameterValue
            image_id = int(image_id)
        except KeyError:
            raise MissingParameter(parameter='ImageId')
        except ValueError:
            raise InvalidAMIID.Malformed

        try:
            none = self.cluster_manager.user.system_image.delete({'system_image_id':image_id})
        except CLMException, error:
            if error.status == 'image_get' or error.status == 'image_unavailable':
                raise InvalidAMIID.NotFound(image_id=image_id)
            if error.status == 'image_delete':
                raise InternalError
            raise UndefinedError

        return {'result': 'true'}


class DescribeImages(Action):

    available_filters = ['description', 'image-id', 'name', 'state']

    def _execute(self):
        GROUP_ACCESS = image_access['group']
        PRIVATE_ACCESS = image_access['private']
        PUBLIC_ACCESS = image_access['public']

        filters = parseFilters( self.parameters )
        if not validateEc2Filters( filters, self.available_filters ):
            raise InvalidFilter

        image_ids = []
        for param, value in self.parameters.iteritems():
            if param.startswith('ImageId'):
                image_id = parseID(value, Entity.image)
                if not image_id:
                    raise InvalidParameterValue
                image_ids.append( image_id )

        images = []
        for access in (PRIVATE_ACCESS, PUBLIC_ACCESS):

            access_images = self.cluster_manager.user.system_image.get_list({
                'access': access,
            })


            for image in access_images:
                if image_ids and str(image.get('image_id')) not in image_ids:
                    continue
                images.append({
                    'description': image.get('description').replace('<', ' '),
                    'image-id': image.get('image_id'),
                    'is_public': 'true' if access == PUBLIC_ACCESS else 'false',
                    'name': image['name'],
                    'owner_id': image.get('user_id'),
                    'platform': PLATFORM.get(image.get('platform')),
                    'state': STATE.get(image.get('state')),
                })

        # listowanie obrazów grupowych - one są zwracane w innej strukturze
        access_images = self.cluster_manager.user.system_image.get_list({'access': GROUP_ACCESS})


        for images_dict in access_images:
            for image in images_dict['images']:
                if image_ids and str(image.get('image_id')) not in image_ids:
                    continue
                images.append({
                    'description': image.get('description').replace('<', ' '),
                    'image-id': image.get('image_id'),
                    'is_public': 'true' if access == PUBLIC_ACCESS else 'false',
                    'name': image['name'],
                    'owner_id': image.get('user_id'),
                    'platform': PLATFORM.get(image.get('platform')),
                    'state': STATE.get(image.get('state')),
                })



        if filters.get('state'):
            for state in filters['state']:
                state = [k for k,v in STATE.iteritems() if v == STATE.get(state) ] # ?? wymaga testu
            del filters['state']

        images = applyEc2Filters(images, filters)
# filtry TODO:
# is-public

        return {'images': images}

class RegisterImage(Action):
    def _execute(self):
        thread.start_new_thread( merge_and_upload, (self.cluster_manager, self.parameters))

        return # TODO zależność od m2crypto i swig

def merge_and_upload(cluster_manager, parameters):
    try:
        manifest_url = parameters['ImageLocation']
    except KeyError, e:
        raise MissingParameter(parameter=e.message)

    image_name = parameters.get('Name')

    # delete slash at the beginning, to join that to BUCKETS_PATH
    if manifest_url.startswith('/'):
        manifest_url = manifest_url[1:]

    user_name = parameters.get('AWSAccessKeyId')

    manifest_path = os.path.join(BUCKETS_PATH, user_name, manifest_url)

    if os.path.abspath(manifest_path) != manifest_path:
        raise InvalidParameter

    parts_directory = os.path.dirname(manifest_path)

    # parse manifest
    dom = minidom.parse(manifest_path)
    manifest_elem = dom.getElementsByTagName('manifest')[0]

    parts = []

    parts_list = manifest_elem.getElementsByTagName('filename')
    for part_elem in parts_list:
        nodes = part_elem.childNodes
        for node in nodes:
            if node.nodeType == node.TEXT_NODE:
                parts.append(node.data)

    encrypted_key_elem = manifest_elem.getElementsByTagName('ec2_encrypted_key')[0]
    encrypted_iv_elem = manifest_elem.getElementsByTagName('ec2_encrypted_iv')[0]

    encrypted_key = encrypted_key_elem.firstChild.nodeValue
    encrypted_iv = encrypted_iv_elem.firstChild.nodeValue

    # concatenate file =========================

    encrypted_filename = manifest_path.replace('.manifest.xml', '.enc.tar.gz')

    if len(parts) > 0:
        encrypted_file = open(encrypted_filename, 'wb')
        for part in parts:
            part_filename = os.path.join(parts_directory, part)
            if not part_filename.startswith(parts_directory):
                raise InvalidManifest

            part_file = open(part_filename, 'rb')
            while 1:
                data = part_file.read(IMAGE_READ_BUFFER)
                if not data:
                    break
                encrypted_file.write(data)
            part_file.close()
        encrypted_file.close()

    # decrypt KEY ==========================
    user_priv_key = RSA.load_key(EC2_PRIVATE_KEY)
    key = user_priv_key.private_decrypt(unhexlify(encrypted_key),
            RSA.pkcs1_padding)
    iv = user_priv_key.private_decrypt(unhexlify(encrypted_iv),
            RSA.pkcs1_padding)
    cipher = EVP.Cipher(alg='aes_128_cbc', key=unhexlify(key),
                   iv=unhexlify(iv), op=0)

    # decrypt image ==========================
    decrypted_filename = encrypted_filename.replace('.enc', '')
    decrypted_file = open(decrypted_filename, 'wb')
    encrypted_file = open(encrypted_filename, 'rb')

    while 1:
        buf = encrypted_file.read(IMAGE_READ_BUFFER)
        if not buf:
            break
        decrypted_file.write(cipher.update(buf))
    decrypted_file.write(cipher.final())

    encrypted_file.close()
    decrypted_file.close()

    # uncompress ======================
    untarred_filename = decrypted_filename.replace('.tar.gz', '')
    tar_file = tarfile.open(decrypted_filename, 'r|gz')
    tar_file.extractall(path=os.path.dirname(untarred_filename))
    tar_file.close()

    link_name = user_name + str(uuid.uuid4())
    link_path = os.path.join(UPLOAD_IMAGES_PATH, link_name)

    # creating symbolic link for use by uploader
    os.symlink(untarred_filename, link_path)

    # generating link used by CM to download image
    image_url = EC2_CM_INTERFACE + '?image_name=' + link_name

    # request CM download =================
    cluster_manager.user.system_image.download({'description': 'Uploaded by EC2',
                                                     'name': image_name,
                                                     'path': image_url,
                                                     'disk_controller': disk_controllers['virtio'],
                                                     'network_device': network_devices['rtl8139'],
                                                     'platform': 0,
                                                     'video_device': video_devices['vga']})
