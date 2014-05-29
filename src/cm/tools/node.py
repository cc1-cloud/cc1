#!/usr/bin/python
# -*- coding: utf-8 -*-
# @cond LICENSE
#
# Copyright [2010-2013] Institute of Nuclear Physics PAN, Krakow, Poland
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
# @endcond LICENSE

"""
@author Maciej Nabozny <mn@mnabozny.pl>
"""

import subprocess
import sys
import os

from cm.utils.exception import CMException
try:
    sys.path.append('/usr/lib/cc1/')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cm.settings")

    from cm.models.node import Node
    from common.states import node_states
except:
    raise CMException('node_cannot_import_model')


# Scripts used to configure distinct systems (especially repositories)
debian_script = '''
if [ -e /etc/apt/sources.list ] ; then
    echo 'deb http://cc1.ifj.edu.pl/packages/ wheezy main #CC1' >> /etc/apt/sources.list
    apt-get update
    apt-get --yes --force-yes install cc1-node cc1-common cc1-common-networking
fi

echo "NODE: Creating cc1 user"
python /usr/sbin/cc1_setup_user create

echo "NODE: Configuring node"
python /usr/sbin/cc1_node_configure configure "%(public_key)s"
'''

def add(address, username, transport, driver, suffix, cpu, memory, disk):
    try:
        Node.objects.get(address=address)
        raise CMException('node_exists')
    except:
        pass

    node = Node()
    node.address = address
    node.comment = ''
    node.driver = driver
    node.transport = transport
    node.username = username
    node.suffix = suffix
    node.cpu_total = cpu
    node.memory_total = memory
    node.hdd_total = disk
    node.state = node_states['offline']
    node.save()

    return 0


def install(node_id, distribution):
    try:
        node = Node.objects.get(id=node_id)
    except:
        raise CMException('node_not_found')

    public_key = open('/var/lib/cc1/.ssh/id_rsa.pub').read()

    # TODO: add password support
    r = -1
    if distribution == 'debian':
        r = subprocess.call(['ssh', '-o', 'PasswordAuthentication=no', 'root@%s' % (node.address),
                             debian_script % {'public_key': public_key}])
    else:
        raise CMException('node_not_implemented')

    if r != 0:
        raise CMException('node_install')
    else:
        return 0


def configure(node_id, interfaces):
    '''
    interfaces - list of interfaces to communicate with cm and other nodes
    '''
    try:
        node = Node.objects.get(id=node_id)
    except:
        raise CMException('node_not_found')

    try:
        sys.path.append('/etc/cc1/cm/')
        import config
    except:
        raise CMException('node_config_invalid')

    cm_ip = 'echo $SSH_CLIENT | cut -d " " -f 1'
    r = subprocess.call(['ssh',
                         '-i',
                         '/var/lib/cc1/.ssh/id_rsa',
                         '%s@%s' % (node.username, node.address),
                         'sudo /usr/sbin/cc1_network_setup configure http://`%s`:8003/ %s %s' % (cm_ip, ','.join(interfaces), config.OSPF_TOKEN)])

    if r != 0:
        raise CMException('node_setup_networking')

    r = subprocess.call(['ssh',
                         '-i',
                         '/var/lib/cc1/.ssh/id_rsa',
                         '%s@%s' % (node.username, node.address),
                         'sudo /usr/sbin/cc1_node_setup_libvirt configure %s %s %s %s %s' %
                         (node.address, node.username, node.transport, node.driver, node.suffix)])
    if r != 0:
        raise CMException('node_setup_libvirt')


def check(node_id):
    try:
        node = Node.objects.get(id=node_id)
    except:
        raise CMException('node_not_found')

    subprocess.call(['ssh', '-i', '/var/lib/cc1/.ssh/id_rsa',
                     '%s@%s' % (node.username, node.address),
                     'sudo /etc/init.d/cc1-node restart'])
