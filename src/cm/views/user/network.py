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

"""@package src.cm.views.user.network
@author Maciej Nabożny <mn@mnabozny.pl>

Functions for creating and deleting networks
"""

from cm.utils.decorators import user_log
from cm.utils import log
from cm.utils.exception import CMException

from cm.models.available_network import AvailableNetwork
from cm.models.user_network import UserNetwork
from cm.models.user import User
from common.states import available_network_states


@user_log(log=True)
def request(caller_id, mask, name):
    """
    Tries to allocate network with specified mask for caller.

    @cmview_user
    @param_post{mask}
    @param_post{name}

    @response{dict} UserNetwork.dict property of the newly created UserNetwork
    """
    new_net = None
    user = User.get(caller_id)
    for available_network in AvailableNetwork.objects.all():
        log.debug(user.id, "Trying to allocate in %s" % str(available_network.to_ipnetwork()))
        if available_network.state == available_network_states['ok']:
            try:
                net = available_network.get_unused_ipnetwork(mask)

                new_net = UserNetwork()
                new_net.address = str(net.network)
                new_net.mask = mask
                new_net.name = name
                new_net.available_network = available_network
                new_net.user = user
                new_net.save()

                new_net.allocate()

                return new_net.dict
            except:
                continue
    if new_net == None:
        raise CMException('available_network_not_found')


@user_log(log=True)
def release(caller_id, network_id):
    """
    When UserNetwork isn't needed anymore, it should be explicitly released
    by User. If UserNetwork is in use, exception is thrown. Released
    UserNetwork is deleted.

    @cmview_user
    @param_post{network_id}
    """
    user = User.get(caller_id)
    try:
        user_network = UserNetwork.objects.filter(user=user).get(id=network_id)
    except:
        raise CMException('network_not_found')

    if user_network.is_in_use():
        raise CMException('network_in_use')
    user_network.release()
    user_network.delete()


@user_log(log=True)
def list_available_networks(caller_id):
    """
    @cmview_user
    @response{list(dict)} AvailableNetwork.dict property for each AvailableNetwork
    """
    available_networks = AvailableNetwork.objects.filter(state=available_network_states['ok'])
    response = []
    for network in available_networks:
        response.append(network.dict)
    return response


@user_log(log=True)
def list_user_networks(caller_id):
    """
    @cmview_user
    @response{list(dict)} UserNetwork.dict property for each caller's
    UserNetwork
    """
    user = User.get(caller_id)
    try:
        user_networks = UserNetwork.objects.filter(user=user)
    except:
        raise CMException('network_not_found')
    response = []
    for network in user_networks:
        if network.available_network.state == available_network_states['ok']:
            response.append(network.dict)
    return response


@user_log(log=True)
def list_leases(caller_id, network_id):
    """
    Returns all Leases in specified UserNetwork

    @cmview_user
    @param_post{network_id} id of the UserNetwork which Leases should be listed
    from
    @response{list(dict)} Lease.dict property for each Lease in specified UserNetwork
    """
    user = User.get(caller_id)
    try:
        user_network = UserNetwork.objects.filter(user=user).get(id=network_id)
    except:
        raise CMException('network_not_found')
    response = []
    for lease in user_network.lease_set.all():
        response.append(lease.dict)
    return response
