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

"""@package src.cm.views.admin_cm.node
@alldecoratedby{src.cm.utils.decorators.admin_cm_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""

from cm.models.node import Node
from cm.utils import log
from cm.utils.decorators import admin_cm_log
from cm.utils.exception import CMException
from common.states import node_states  # , lease_states
from cm.tools import node as node_tools


@admin_cm_log(log=True)
def add(caller_id, address, username, transport, driver, suffix, cpu, memory, disk):
    """
    Adds new Node to this Cluster. Node must be a machine preconfigured to be
    CC1 node.

    @cmview_admin_cm
    @param_post{username,string} Node's operating system username for
    transport. Should be @val{cc1}.
    @param_post{address,string} added Node IP adress or domain name
    @param_post{transport,string} @val{unix}, @val{ssh}, @val{tls} or other
    available transport name for hypervisor
    @param_post{suffix,string} optional suffix for transport (i.e. /system for KVM)
    @param_post{driver,string} hypervisior name (XEN, KVM or other, KVM is
    recommended)
    @param_post{cpu,int}
    @param_post{memory,int}
    @param_post{disk,int}

    @note Not used (but might be used one day)
    """
    try:
        node_tools.add(address, username, transport, driver, suffix, cpu, memory, disk)
    except Exception, e:
        log.error(caller_id, 'Cannot add node: %s' % str(e))
        raise CMException(str(e))


@admin_cm_log(log=True)
def install(caller_id, node_id, distribution):
    """
    @cmview_admin_cm
    @param_post{node_id,int} id of the Node where cc1-node should be deployed
    @param_post{distribution,string} OS distribution name, e.g. Debian

    @note Not used (but might be used one day)
    """
    try:
        node_tools.install(node_id, distribution)
    except Exception, e:
        log.error(caller_id, 'Cannot install node: %s' % str(e))
        raise CMException(str(e))


@admin_cm_log(log=True)
def configure(caller_id, node_id, interfaces):
    """
    @cmview_admin_cm
    @param_post{node_id,int} node id
    @param_post{interfaces,string list} list of interfaces, which node should
    use to communicate with other nodes and cm.

    @note Not used (but might be used one day)
    """
    try:
        node_tools.configure(node_id, interfaces)
    except Exception, e:
        log.error(caller_id, 'Cannot configure node: %s' % str(e))
        raise CMException(str(e))


@admin_cm_log(log=True)
def check(caller_id, node_id_list):
    """
    Tries to restart cc1-node service on each specified Node

    @cmview_admin_cm
    @param_post{node_id_list,list(int)}

    @note Not used (but might be used one day)
    """
    try:
        for node_id in node_id_list:
            node_tools.check(node_id)
    except Exception, e:
        log.error(caller_id, 'Cannot check node: %s' % str(e))
        raise CMException(str(e))


@admin_cm_log(log=False)
def get_list(caller_id):
    """
    @cmview_admin_cm
    @response{list(dict)} Node.dict property for each Node added to current CM
    """
    return [node.dict for node in Node.objects.exclude(state__exact=node_states['deleted'])]


@admin_cm_log(log=True)
def get_by_id(caller_id, node_id):
    """
    Returns details of the requested Node.

    @cmview_admin_cm
    @param_post{node_id,int} id of the requested Node
    @response{dict} Node.long_dict property of the requested Node
    """
    node = Node.get(caller_id, node_id)
    return node.long_dict


@admin_cm_log(log=True)
def get_by_id_details(caller_id, node_id):
    """
    Returns more details of the requested Node.

    @cmview_admin_cm
    @param_post{node_id,int} id of the requested Node
    @response{dict} Node.long_long_dict property of the requested Node
    """
    node = Node.get(caller_id, node_id)
    return node.long_long_dict


@admin_cm_log(log=True)
def lock(caller_id, node_id_list):
    """
    Sets specified Node's state as @val{locked}. No VMs can be run on locked Node.

    @cmview_admin_cm
    @param_post{node_id_list,int} list of the specified Nodes ids

    @response{None}

    @raises{node_lock,CMException}
    """
    for node_id in node_id_list:
        node = Node.get(caller_id, node_id)
        node.state = node_states['locked']

        try:
            node.save()
        except:
            raise CMException('node_lock')


@admin_cm_log(log=True)
def unlock(caller_id, node_id_list):
    """
    Unlocks specified Node. After unlock Node's state is @val{ok} and Users
    are able to run VMs on that Node.

    @cmview_admin_cm
    @param_post{node_id_list,int} list of the specified Nodes ids

    @response{None}

    @raises{node_unlock,CMException}
    """

    for node_id in node_id_list:
        node = Node.get(caller_id, node_id)
        node.state = node_states['ok']

        try:
            node.save()
        except:
            raise CMException('node_unlock')


@admin_cm_log(log=True)
def delete(caller_id, node_id):
    """
    Deletes specified Node from database provided the Node does not host any
    VM's. Node's operating system setup isn't affected. To bring deleted Node
    back available for CC1 Cluster, one has to add it once again via Web
    Interface.

    @cmview_admin_cm
    @param_post{node_id,int} id of the Node to delete

    @raises{node_has_vms,CMException}
    @raises{node_delete,CMException}
    """
    node = Node.get(caller_id, node_id)

    # check if the node has vms
    if node.vm_set.exists():
        raise CMException('node_has_vms')

    try:
        node.delete()
    except:
        raise CMException('node_delete')


# edits node, according to data provided in node_info
@admin_cm_log(log=True)
def edit(caller_id, node_id, **node_info):
    """
    Updates Node attributes according to data provided in node_info.

    @cmview_admin_cm
    @param_post{node_id,int} id of the Node to edit
    @param_post{node_info,string} dictionary where cm.models.Node model's
    fields are the keys and values are values to set

    @raises{node_edit,CMException}
    """
    node = Node.get(caller_id, node_id)

    for k, v in node_info.iteritems():
        setattr(node, k, v)

    try:
        node.save()
    except:
        raise CMException('node_edit')
