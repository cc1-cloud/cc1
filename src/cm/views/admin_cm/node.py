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


# from cm.database.entities.user_network import UserNetwork
# from cm.database.entities.available_network import AvailableNetwork
# from cm.database.entities.lease import Lease
# from common import response, vnc_states
# from common.utils import xml2dict, ip_stoi, ip_itos
# from ..monia.threads import start_monia
# import libvirt
@admin_cm_log(log=True)
def add(caller_id, **node_info):
    """
    Method adds new Node to the Cluster.
    Node must be machine configured as CC1 node.
    @cmview_admin_cm

    @parameter{username,string} optional username for transport
    @parameter{address,string} node ip adress or domain name
    @parameter{transport,string} unix, ssh, tls or other available transport name for kvm
    @parameter{driver,string} XEN, KVM or other hypervisior name
    @parameter{cpu_total,int}
    @parameter{memory_total,int}
    @parameter{hdd_total,int}
    @parameter{suffix,string} optional suffix for transport (i.e. /system for KVM)
    @parameter{comment,string}
    """
    node = Node()

    node.username = node_info['username']
    node.address = node_info['address']
    node.transport = node_info['transport']
    node.driver = node_info['driver']
    node.cpu_total = node_info['cpu_total']
    node.memory_total = node_info['memory_total']
    node.hdd_total = long(node_info['hdd_total'])
    node.suffix = node_info['suffix']
    node.comment = node_info['comment']

    node.state = node_states['ok']

    # Session.add(node)

    # Session.flush()

    # add network
    # try:
    #    conn = libvirt.open(node.conn_string)
    # except:
    #    log.exception(user_id, 'node_lv_open')
    #    raise CMException('node_lv_open')
    # n = conn.networkLookupByName(node_info['network'])
    # xml = n.XMLDesc(0)
    # d = xml2dict(xml)
    # start = ip_stoi(d.get('network').get('ip').get('dhcp').get('range').get('start'))
    # end = ip_stoi(d.get('network').get('ip').get('dhcp').get('range').get('end'))

    # network = Network()
    # network.node_id = node.id
    # network.name = node_info['network']
    # Session.add(network)

    # try:
    #    for ip in range(start, end+1):
    #        lease = Lease()
    #        lease.network = network
    #        lease.ip = ip_itos(ip)
    #        lease.state = lease_states['free']
    #        Session.add(lease)
    # except:
    #    log.exception(user_id, 'lease_create')
    #    raise CMException('lease_create')

    try:
        node.save()
        # TODO: monia
        # start_monia()  # odswiezenie listy nodow w monitoringu / refresh monitoring
    except:
        log.exception(caller_id, 'node_create')
        raise CMException('node_create')


# returns list of added nodes
@admin_cm_log(log=False)
def get_list(caller_id):
    """
    @cmview_admin_cm
    Method returns list of added nodes.
    @cmview_admin_cm

    @response{list(dict)} dicts describing nodes
    """
    return [node.dict for node in Node.objects.exclude(state__exact=node_states['deleted'])]


# TODO:
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# def list_network(user_id, node_id):
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@admin_cm_log(log=True)
def get_by_id(caller_id, node_id):
    """
    Method returns requested Node.
    @decoratedby{src.cm.utils.decorators.admin_cm_log}

    @parameter{caller_id,int}
    @parameter{node_id,int} id of the requested Node

    @response{dict} extended information about Node
    """
    node = Node.get(caller_id, node_id)  # use static method get by Node
    return node.long_dict


@admin_cm_log(log=True)
def get_by_id_details(caller_id, node_id):
    """
    Method returns detailed of requested Node.
    @decoratedby{src.cm.utils.decorators.admin_cm_log}

    @parameter{node_id,int} id of the requested Node

    @response{dict} further extended information about Node
    """
    node = Node.get(caller_id, node_id)  # use static method get by Node
    return node.long_long_dict


@admin_cm_log(log=True)
def lock(caller_id, node_id):
    """
    Method locks specified Node. No VMs can be run on locked node.
    @decoratedby{src.cm.utils.decorators.admin_cm_log}

    @parameter{caller_id,int}
    @parameter{node_id,int} id of the Node to lock

    @response{None}

    @raises{node_lock,CMException}
    """
    node = Node.get(caller_id, node_id)
    node.state = node_states['locked']

    try:
        node.save()
        # TODO:
        # start_monia()
    except:
        raise CMException('node_lock')


@admin_cm_log(log=True)
def unlock(caller_id, node_id):
    """
    Method unlocks specified Node. After unlock Node's state is @val{ok} and
    one is be able to run VMs on that Node.
    @decoratedby{src.cm.utils.decorators.admin_cm_log}

    @parameter{caller_id,int}
    @parameter{node_id,int} id of the Node to unlock

    @response{None}

    @raises{node_unlock,CMException}
    """
    node = Node.get(caller_id, node_id)
    node.state = node_states['ok']

    try:
        node.save()
        # TODO:
        # start_monia()
    except:
        raise CMException('node_unlock')


@admin_cm_log(log=True)
def delete(caller_id, node_id):
    """
    Method deletes specified Node (provided it's state isn't  @val{closed}).
    To bring deleted Node back available for CC1 system, one has to add it once
    again.
    @decoratedby{src.cm.utils.decorators.admin_cm_log}

    @parameter{caller_id,int}
    @parameter{node_id,int} id of the node to delete

    @response{None}

    @raises{node_has_vms,CMException}
    @raises{node_delete,CMException}
    """
    node = Node.get(caller_id, node_id)

    # check if the node has vms
    if node.vm_set.exists():
        raise CMException('node_has_vms')

    try:
        node.delete()
        # TODO:
        # start_monia()  # odswiezenie listy nodow w monitoringu
    except:
        raise CMException('node_delete')


# edits node, according to data provided in node_info
@admin_cm_log(log=True)
def edit(caller_id, node_id, **node_info):
    """
    Method edits node, according to data provided in request,data.
    @decoratedby{src.cm.utils.decorators.admin_cm_log}. All Node's attributes
    need to be present in data dictionary (even if only some of
    them are changed, e.g. driver). Former Node's attributes may be accessed via
    clm.views.admin_cm.node.get_by_id() method.

    @parameter{caller_id,int}
    @parameter{driver,string} xen, kvm or other hypervisior name
    @parameter{transport,string} unix, ssh, tls or other available transport name for kvm
    @parameter{address,string} node ip adress or domain name
    @parameter{username,string} optional username for transport
    @parameter{suffix,string} optional suffix for transport (i.e. /system for KVM)
    @parameter{cpu_total,int}
    @parameter{memory_total,int}
    @parameter{hdd_total,int}
    @parameter{node_id} id of the Node to edit

    @response{None}

    @raises{node_edit,CMException}
    """
    node = Node.get(caller_id, node_id)

    # set the values sent in dictionary
    for k, v in node_info.iteritems():
        # if hasattr(node, k):
        setattr(node, k, v)

    try:
        node.save()
        # TODO:
        # start_monia()  # odswiezenie listy nodow w monitoringu
    except:
        raise CMException('node_edit')
