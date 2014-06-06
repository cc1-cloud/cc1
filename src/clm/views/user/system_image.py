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

"""@package src.clm.views.user.image
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from clm.models.user import User
from common.states import image_access, group_states
from clm.utils.decorators import user_log, cm_request
from clm.utils.cm import CM
from clm.utils.exception import CLMException
import json


@user_log(log=False)
def get_list(cm_id, caller_id, **data):
    """
    Method returns list of images.

    @parameter{data,dict}
    \n fields as described by src.cm.views.user.image.list()

    @returns{list(dict)}
    images: {gid, name, [images]}
    """
    group_dict = {}

    # creation of information in data['gid']: group ids the caller belongs to
    if data['access'] == image_access['group']:
        groups = User.get(caller_id).group_set.filter(usergroup__status__exact=group_states['ok'])
        data['group_id'] = []
        for g in groups:
            # append info in data['gid'] to send with the request to CM
            data['group_id'].append(int(g.id))
            group_dict[g.id] = {'name': g.name, 'images': []}

    resp = CM(cm_id).send_request("user/system_image/get_list/", caller_id=caller_id, **data)
    if resp['status'] != 'ok':
        return resp

    images = resp['data']
    # uzupełnianie zapytania o ownera i grupowanie w słownik {gid, name, [images]}
    # adds information on the owner of the images with group access {gid, name, [images]}
    if data['access'] == image_access['group']:
        d = {}
        for img in images:
            group_dict[img['group_id']]['images'].append(img)

            if img['user_id'] not in d:
                try:
                    u = User.objects.get(pk=img['user_id'])
                    d[img['user_id']] = u.first + " " + u.last
                except:
                    raise CLMException('user_get')
            img['owner'] = d[img['user_id']]
        resp = [{'group_id': k, 'name': v['name'], 'images': v['images']} for k, v in group_dict.iteritems()]

        return resp

    return images


@user_log(log=False, pack=False)
def get_by_id(cm_id, caller_id, **data):  # @todo rename for fun name consistency
    """
    @parameter{id,int} managed image's id
    """
    user = User.get(caller_id)
    groups = list(user.group_set.filter(usergroup__status__exact=group_states['ok']).values_list('id', flat=True))
    return CM(cm_id).send_request("user/system_image/get_by_id/", caller_id=caller_id, groups=groups, **data)


@user_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @parameter{id,int} managed image's id
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def edit(cm_response, **data):
    """
    @parameter{id,int} managed image's id
    @parameter{data,dict}
    \n fields:
    @dictkey{name,string}
    @dictkey{description,string}
    - platform
    """
    return cm_response


@user_log(log=True, pack=False)
def set_private(cm_id, caller_id, system_image_id):
    """
    @parameter{id,int} managed image's id
    """
    user = User.get(caller_id)
    return CM(cm_id).send_request("user/system_image/set_private/", caller_id=caller_id, system_image_id=system_image_id,
                                  leader_groups=[g.id for g in user.own_groups])


@user_log(log=True, pack=False)
@cm_request
def set_group(cm_response, **data):
    """
    @parameter{img_id,int} managed image's id
    @parameter{data,dict}
    \n fields:
    @dictkey{group_id,int}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def create(cm_response, **data):
    """
    @parameter{data,dict}
    \n fields:
    @dictkey{size,int}
    - type
    - access
    @dictkey{user_id,int}
    @dictkey{name,string}
    @dictkey{description,string}
    @dictkey{platform} optional
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def download(cm_response, **data):
    """
    @parameter{data,dict}
    \n fields:
    - path
    - type
    @dictkey{access} optional (default: private)
    - name
    - description
    - platform
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_filesystems(cm_response, **data):
    """
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_video_devices(cm_response, **data):
    """
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_network_devices(cm_response, **data):
    """
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_disk_controllers(cm_response, **data):
    """
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def convert_to_storage_image(cm_response, **data):
    """
    """
    return cm_response
