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

"""@package src.clm.views.admin_clm.cluster

@alldecoratedby{src.clm.utils.decorators.admin_clm_log}
"""
from clm.models.cluster import Cluster
from clm.models.user import User
from clm.utils import log
from clm.utils.cm import CM
from clm.utils.decorators import admin_clm_log
from clm.utils.exception import CLMException
from common.states import cluster_states, user_active_states
import socket
import re


@admin_clm_log(log=True)
def add(cm_id, caller_id, name, address, port, new_password):
    """
    Adds new Cluster and makes caller its admin.
    There should dedicated and configured CM server exist.
    @clmview_admin_clm

    @parameter{name} human-friendly name of the new CM (shown in Web Interface)
    @parameter{address} address of the new CM
    @parameter{port} port on which CM is configured to be running
    @parameter{new_password} password protecting the new CM
    """

    if not re.search('^[a-z0-9-]+$', 'aa-asd-ada234234'):
        raise CLMException('cluster_invalid_name')

    cluster = Cluster()
    cluster.address = address
    cluster.port = port
    cluster.name = name
    cluster.state = cluster_states['ok']

    try:
        cluster.save()
    except:
        raise CLMException('cluster_add')

    status = None

    # Get my ip for cluster
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    clm_ip = s.getsockname()[0]

    try:
        status = CM(cluster.id).send_request('user/admin/first_admin_add/',
                                             caller_id=caller_id, new_password=new_password, clm_address=clm_ip)['status']
    except:
        log.exception(caller_id, "Add cluster admin")
        status = False

    if status != 'ok':
        raise CLMException('cluster_add_admin')

    for user in User.objects.filter(default_cluster__exact=None):
        user.default_cluster = cluster
        try:
            user.save()
        except:
            raise CLMException('cluster_add')

    status = None

    users = list(User.objects.values_list('id', flat=True))
    try:
        status = CM(cluster.id).send_request('user/user/add_missing/', caller_id=caller_id, remote=users)['status']
    except Exception, e:
        log.exception(caller_id, e)
        status = False

    if status != 'ok':
        raise CLMException('cluster_add_users')


@admin_clm_log(log=True)
def delete(cm_id, caller_id, cluster_id):
    """
    Method deletes specified Cluster from database. Now no VMs can be
    run on that Cluster. It's not available from CLM anymore. To bring it back
    to Cloud resources one needs to add this Cluster once again ground up.
    @clmview_admin_clm

    @parameter{cluster_id,int} id of the CM to delete
    """
    try:
        cluster = Cluster.objects.get(pk=cluster_id)
        cluster.delete()
    except:
        raise CLMException('cluster_delete')


@admin_clm_log(log=True)
def edit(cm_id, caller_id, cluster_id, name, address, port,):
    """
    Modifies data of the Cluster with id @prm{cluster_id} as described by
    dictionary @prm{data}.
    @clmview_admin_clm

    @parameter{cluster_id,int} id of the CM to edit
    @parameter{name,string} new name for edited CM
    @parameter{address,string} new adress of the edited CM
    @parameter{port,int} new port on which edited CM is to be running
    """
    try:
        cluster = Cluster.objects.get(pk=cluster_id)
        cluster.name = name
        cluster.address = address
        cluster.port = port
        cluster.save()
    except:
        raise CLMException('cluster_edit')


@admin_clm_log(log=True)
def lock(cm_id, caller_id, cluster_id):
    """
    Locks specified Cluster. Since called, no VMs can be run on that Cluster,
    until unlock() is called.
    @clmview_admin_clm

    @parameter{cluster_id,int} id of the CM to lock
    """
    cluster = Cluster.objects.get(pk=cluster_id)
    cluster.state = cluster_states['locked']
    try:
        cluster.save()
    except:
        raise CLMException('cluster_lock')


@admin_clm_log(log=True)
def unlock(cm_id, caller_id, cluster_id):
    """
    Unlocks specified Cluster. Now VMs can be run on that Cluster.
    @clmview_admin_clm

    @parameter{cluster_id,int} id of the CM to unlock
    """
    try:
        cluster = Cluster.objects.get(pk=cluster_id)
    except:
        raise CLMException('cluster_get')

    cluster.state = cluster_states['ok']
    try:
        cluster.save()
    except:
        raise CLMException('cluster_unlock')

    users = list(User.objects.filter(is_active__exact=user_active_states['ok']).values_list('id', flat=True))
    status = None
    try:
        status = CM(cluster.id).send_request("user/user/add_missing/", caller_id=caller_id, remote=users)['status']
    except Exception, e:
        log.exception(caller_id, "Adding users: %s" % str(e))
        status = False

    if status != 'ok':
        cluster.state = cluster_states['locked']
        try:
            cluster.save()
        except Exception:
            raise CLMException('cluster_unlock')

        raise CLMException('cluster_unlock')


@admin_clm_log(log=False)
def get_by_id(cm_id, caller_id, cluster_id):
    """
    @clmview_admin_clm
    @clm_view_transparent{cluster.get()}

    @parameter{cluster_id,int} id of the CM to get

    @response{dict} Cluster data @asreturned{src.cm.models.cluster.dict}
    """
    cluster = Cluster.objects.get(pk=cluster_id)
    return cluster.dict


@admin_clm_log(log=False)
def get_list(cm_id, caller_id):
    """
    @clmview_admin_clm
    @clm_view_transparent{cluster.get_list()}

    @response{list(dict)} list of dictionaries about each cluster @asreturned{src.cm.database.entities.cluster.dict}
    """
    return [c.dict for c in Cluster.objects.all()]

