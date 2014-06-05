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

"""@package src.clm.views.admin_cm.image
@alldecoratedby{src.clm.utils.decorators.admin_cm_log}
"""

import json

from clm.models.group import Group
from clm.models.user import User
from clm.utils.cm import CM
from clm.utils.decorators import admin_cm_log, cm_request
from clm.utils.exception import CLMException
from common.states import image_access, group_states


@admin_cm_log(log=False, pack=True)
def get_list(cm_id, caller_id, **data):
    """
    Admin function to list images.

    @parameter{cm_passwd,string} caller's *CM admin password*
    @parameter{data,dict}
    \n fields:
    @dictkey{access,int} number representing image access:
        - 0: private
        - 1: public
        - 2: group
    @dictkey{group_id,int} required if \c access is 2
    @dictkey{user_id,int}
    """
    if data['access'] == image_access['group']:
        groups = Group.objects.all()
        if data.get('group_id', None):
            groups = groups.objects.filter(id__exact=data['group_id'])
        if data.get('group_id', None):
            groups = groups.filter(usergroup__user_id__exact=data['user_id']).filter(usergroup__status__exact=group_states['ok'])

        data['group_id'] = []
        r = {}
        for g in groups:
            data['group_id'].append(int(g.id))
            r[g.id] = {'name': g.name, 'images': []}

    resp = CM(cm_id).send_request("admin_cm/system_image/get_list/", caller_id=caller_id, **data)

    d = {}
    for img in resp['data']:
        if str(img['user_id']) not in d:
            try:
                u = User.objects.get(pk=img['user_id'])
                d[str(img['user_id'])] = u.first + " " + u.last
            except:
                raise CLMException('user_get')
        img['owner'] = d[str(img['user_id'])]

    if data['access'] == image_access['group']:
        d = {}
        for img in resp['data']:
            r[img['group_id']]['images'].append(img)

            if img['user_id'] not in d:
                try:
                    u = User.objects.get(pk=img['user_id'])
                    d[img['user_id']] = u.first + " " + u.last
                except:
                    raise CLMException('user_get')
            img['owner'] = d[img['user_id']]
        r = [{'group_id': k, 'name': v['name'], 'images': v['images']} for k, v in r.iteritems()]

        return r

    return resp['data']


@admin_cm_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):
    """
    @clmview_admin_cm
    @clm_view_transparent{system_image.get_by_id()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @clmview_admin_cm
    @clm_view_transparent{system_image.delete()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def edit(cm_response, **data):
    """
    @clmview_admin_cm
    @clm_view_transparent{system_image.edit()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def download(cm_response, **data):
    """
    @clmview_admin_cm
    @clm_view_transparent{system_image.download()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def copy(cm_response, **data):
    """
    @clmview_admin_cm
    @clm_view_transparent{system_image.copy()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def set_public(cm_response, **data):
    """
    @clmview_admin_cm
    @clm_view_transparent{system_image.set_public()}
    """
    return cm_response


@admin_cm_log(log=True, pack=False)
@cm_request
def set_private(cm_response, **data):
    """
    @clmview_admin_cm
    @clm_view_transparent{system_image.set_private()}
    """
    return cm_response
