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
"""@package src.cm.views.admin_cm.network
@author Maciej Nabożny <mn@mnabozny.pl>

Functions for creating and deleting networks.
"""
from cm.models.user_network import UserNetwork
from cm.models.available_network import AvailableNetwork
from cm.models.user import User
from cm.utils.exception import CMException
from cm.utils.decorators import admin_cm_log
from common.states import available_network_states

from netaddr import IPNetwork


@admin_cm_log(log=True)
def add(caller_id, address, mask):
    networks = []
    for net in AvailableNetwork.objects.all():
        networks.append(net.to_ipnetwork())
    networks.sort()

    # Find duplicate
    ipnet = IPNetwork('%s/%d' % (address, mask))
    for i in xrange(len(networks)):
        if ipnet.prefixlen > networks[i].prefixlen and ipnet > networks[i].previous() and ipnet < networks[i].next():
            raise CMException('network_exists')
        elif ipnet.prefixlen < networks[i].prefixlen and ipnet.previous() < networks[i] and ipnet.next() > networks[i]:
            raise CMException('network_exists')

    # Add new network
    new_net = AvailableNetwork()
    new_net.address = ipnet.network
    new_net.mask = mask

    if ipnet.is_private():
        new_net.state = available_network_states['ok']
    else:
        new_net.state = available_network_states['locked']

    new_net.save()


@admin_cm_log(log=True)
def delete_available_network(caller_id, pool_id):
    """
    Releases and deletes AvailableNetwork (if not used).

    @cmview_admin_cm
    @param_post{pool_id,int} id of the AvailableNetwork to delete
    """
    try:
        net = AvailableNetwork.objects.get(id=pool_id)
    except:
        raise CMException('available_network_not_found')
    net.release()
    net.delete()


@admin_cm_log(log=True)
def delete_user_network(caller_id, network_id):
    """
    Releases and deletes UserNetwork (if not used).

    @cmview_admin_cm
    @param_post{network_id,int} id of the UserNetwork to delete
    """
    try:
        net = UserNetwork.objects.get(id=network_id)
    except:
        raise CMException('network_not_found')
    net.release()
    net.delete()


@admin_cm_log(log=True)
def list_available_networks(caller_id):
    """
    @cmview_admin_cm
    @response{list(dict)} AvailableNetwork.dict property for each requested AvailableNetwork
    """
    response = []
    for network in AvailableNetwork.objects.all():
        response.append(network.dict)
    return response


@admin_cm_log(log=True)
def list_user_networks(caller_id, user_id=None):
    """
    @cmview_admin_cm
    @param_post{user_id,int} (optional) if specified, only networks belonging
    to specigied User are fetched.
    @param_post{only_unused,bool} (optional) if @val{True}, only unused
    networks are returned

    @response{list(dict)} UserNetwork.dict property for each requested
    UserNetwork
    """
    try:
        user_networks = []
        if user_id:
            user = User.get(user_id)
            user_networks = UserNetwork.objects.filter(user=user)
        else:
            user_networks = UserNetwork.objects.all()
    except:
        raise CMException('network_not_found')

    response = []
    for network in user_networks:
        response.append(network.dict)
    return response


@admin_cm_log(log=True)
def list_leases(caller_id, network_id):
    """
    @cmview_admin_cm
    @param_post{network_id} id of the requested UserNetwork

    @response{list{dict}} Lease.dict property for each Lease in specified
    UserNetwork
    """
    try:
        user_network = UserNetwork.objects.get(id=network_id)
    except:
        raise CMException('network_not_found')

    response = []
    for lease in user_network.lease_set.all():
        response.append(lease.dict)
    return response


@admin_cm_log(log=True)
def lock(caller_id, pool_id):
    """
    Sets AvailableNetwork's state as @val{locked}.

    @cmview_admin_cm
    @param_post{pool_id,int} id of the AvailableNetwork to lock
    """
    try:
        network = AvailableNetwork.objects.get(id=pool_id)
    except:
        raise CMException('available_network_not_found')
    network.state = available_network_states['locked']
    network.save()


@admin_cm_log(log=True)
def unlock(caller_id, pool_id):
    """
    Sets AvailableNetwork's state as @val{ok}.

    @cmview_admin_cm
    @param_post{pool_id,int} id of the AvailableNetwork to unlock
    """
    try:
        network = AvailableNetwork.objects.get(id=pool_id)
    except:
        raise CMException('available_network_not_found')
    network.state = available_network_states['ok']
    network.save()
