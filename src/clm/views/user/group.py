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

"""@package src.clm.views.user.group
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from clm.models.user import User
from clm.models.group import Group
from clm.models.user_group import UserGroup
from clm.models.message import Message
from clm.utils import log, message
from clm.utils.cm import CM
from clm.utils.decorators import user_log
from clm.utils.exception import CLMException
from common.states import group_states, image_access  # , image_types
import json


@user_log(log=True)
def create(cm_id, caller_id, name, description):
    """
    Method creates new users Group. Sets caller as leader of that group.
    Sets membership's state to 'ok'.
    @clmview_user

    @parameter{name,string}
    @parameter{description,string}
    """
    user = User.get(caller_id)

    # create group
    group = Group()
    group.leader = user
    group.name = name
    group.desc = description
    group.save()

    # create first membership
    mem = UserGroup()
    mem.user = user
    mem.group = group
    mem.status = group_states['ok']
    try:
        mem.save()
    except:
        raise CLMException('group_create')


@user_log(log=True)
def join_request(cm_id, caller_id, group_id):
    """
    Method sends request for acceptation in group @prm{group_id} for caller.
    Adds caller to members  with 'waiting' state.
    @clmview_user

    @parameter{group_id,int} id of the Group, which caller wants to become member of
    """
    group = Group.get(group_id)
    user = User.get(caller_id)

    mem = UserGroup()
    mem.user = user
    mem.group = group
    mem.status = group_states['waiting']

    message.info(group.leader_id, 'group_request', params={'first_name': user.first, 'last_name': user.last, 'group_name': group.name, 'group_id': group.id})
    try:
        mem.save()
    except:
        raise CLMException('group_request')


@user_log(log=False)
def get_list(cm_id, caller_id):
    """
    Method returns list of all the existing groups. To dictionary about each
    Group there is info about membership status appended - 'ok', 'waiting'
    or 'not member'.
    @clmview_user

    @response{list(dict)} all Groups
    """
    user = User.get(caller_id)
    waiting = []
    ok = []

    for ug in UserGroup.objects.filter(user_id__exact=user.id):
        if ug.status == group_states['waiting']:
            waiting.append(ug.group_id)
        elif ug.status == group_states['ok']:
            ok.append(ug.group_id)
    groups = []
    for g in Group.objects.all():
        d = g.dict
        if g.id in ok:
            d['user_status'] = group_states['ok']
        elif g.id in waiting:
            d['user_status'] = group_states['waiting']
        else:
            d['user_status'] = group_states['not member']
        groups.append(d)

    return groups


@user_log(log=False)
def list_groups(cm_id, caller_id):
    """
    Method returns list of the groups caller belongs to with 'ok' state.
    @clmview_user

    @response{list(dict)} caller's Groups
    """
    user = User.get(caller_id)
    groups = []
    for g in user.group_set.all():
        d = g.dict
        d['status'] = group_states['ok']
        groups.append(d)

    return groups


@user_log(log=False)
def list_members(cm_id, caller_id, group_id):
    """
    Method returns members of the group with id @prm{group_id}.
    @clmview_user

    @parameter{group_id,int} id of the Group that we get list of

    @response{list(dict)} dicts describing users belonging to specifie group.
    """

    # group_id is sent in the URL
    group = Group.objects.get(pk=group_id)

    return [u.dict for u in group.users.filter(usergroup__status__exact=group_states['ok'])]


@user_log(log=True)  # XXX
def list_own_groups(cm_id, caller_id):
    """
    Method returns list of the groups caller is leader of.
    @clmview_user

    @response{list(dict)} dicts describing groups led by caller
    """
    user = User.get(caller_id)

    # returns all the groups where the user is the leader
    return  [g.dict for g in user.own_groups]


@user_log(log=False)
def list_requests(cm_id, caller_id, group_id):
    """
    Function returns list of the users requesting acceptation
    in group with id @prm{group_id}.
    @clmview_user

    @parameter{group_id,int} id of the group which we check membership
    requests for

    @response{list(dict)} dicts describing requesting users
    """

    # group_id is sent in the URL
    group = Group.objects.get(pk=group_id)

    return [u.dict for u in group.users.filter(usergroup__status__exact=group_states['waiting'])]


@user_log(log=True)
def delete(cm_id, caller_id, group_id):
    """
    Method deletes specified Group.
    @clmview_user

    @parameter{group_id,int} id of the Group to delete
    """

    group = Group.get(group_id)

    resp = CM(cm_id).send_request("user/system_image/get_list/", caller_id=caller_id, group_id=[group_id], access=image_access['group'])
    if resp['status'] != 'ok':
        return resp['data']

    log.debug(caller_id, 'groups %s' % resp)

    user = User.get(caller_id)
    # # set private all the system images that belong to the group
    for img in resp['data']:
    #     print img
        resp = CM(cm_id).sendRequest(cm_id, caller_id, "user/system_image/set_private/", system_image_id=img['image_id'], leader_groups=[g.group_id for g in user.own_groups])
        # r = cm(cm_id).image.user.set_private(caller_id, img['id'], {'leader_groups': [g.id for g in user.own_groups]})
    #     # unjson response to check status
    #     resp = json.loads(r.content)
    #
        log.debug(caller_id, 'image set private %s' % resp['data'])
        if resp['status'] != 'ok':
            return resp['data']
    #
    try:
        group.delete()
    except:
        raise CLMException('group_delete')


@user_log(log=True)
def edit(cm_id, caller_id, group_id, name, description):
    """
    Method edits specified Group.

    @dictkey{group_id,string} id of the group to edit
    @dictkey{name,string} group's name
    @dictkey{description,string} group's description
    """
    group = Group.get(group_id)
    group.name = name
    group.desc = description
    try:
        group.save()
    except:
        raise CLMException('group_edit')


# TODO: not tested
@user_log(log=False)
def activate_user(cm_id, caller_id, user_id, group_id):
    """
    Method activates @prm{user_id} user in group @prm{group_id}. Activated
    user gains access to IsoImage-s shared by that group.

    @parameter{id,int} id of the group in which user must be activated
    @parameter{user_id,int} id of the user to activate
    """
    # check that the caller is leader
    User.is_leader(caller_id, group_id)

    try:
        mem = UserGroup.objects.filter(group_id__exact=group_id).filter(user_id__exact=user_id).filter(status__exact=group_states['waiting'])[0]
    except:
        raise CLMException('user2group_get')

    mem.status = group_states['ok']
    for m in Message.objects.filter(user_id__exact=caller_id).filter(code__exact='group_request'):
        if json.loads(m.params).get('group_id', None) == id:
            m.delete()
    try:
        mem.save()
    except:
        raise CLMException('user_activate')


@user_log(log=True)
def delete_user(cm_id, caller_id, user_id, group_id):
    """
    Method deletes membership of the specified user in specific group,

    @parameter{user_id,int} id of the user to delete from group
    @parameter{group_id,int} id of the managed group
    """
    if caller_id != user_id:
        User.is_leader(caller_id, group_id)

    try:
        mem = UserGroup.objects.filter(group_id__exact=group_id).filter(user_id__exact=user_id)[0]
    except:
        raise CLMException('user2group_get')

    for m in Message.objects.filter(user_id__exact=caller_id).filter(code__exact='group_request'):
        log.debug(caller_id, 'message params %s' % m.params)
        if json.loads(m.params).get('group_id', None) == id:
            log.debug(caller_id, 'delete message for group %s' % id)
            m.delete()

    try:
        mem.delete()
    except:
        raise CLMException('group_delete_user')


@user_log(log=True)
def change_owner(cm_id, caller_id, user_id, group_id):
    """
    Function changes owner of the specified group. Only owner may be the caller,
    otherwise exception is thrown. @prm{user_id} becomes new Group's leader.

    @parameter{user_id,int} id of the new owner
    @parameter{group_id,int} id of the managed Group
    """
    # check that the caller is leader
    User.is_leader(caller_id, group_id)

    group = Group.get(group_id)
    new_leader = User.get(user_id)

    group.leader = new_leader

    try:
        group.save()
    except:
        raise CLMException('group_change_owner')


@user_log(log=False)
def get_by_id(cm_id, caller_id, group_id):
    """
    Method returns requested group.

    @parameter{group_id,int} id of the requested Group

    @response{dict} requested Group's details
    """

    return Group.get(group_id).dict
