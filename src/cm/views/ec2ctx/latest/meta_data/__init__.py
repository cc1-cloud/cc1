# _*_ coding: utf_8 _*_
# @COPYRIGHT_begin
#
# Copyright [2010_2013] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE_2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end
from cm.models.vm import VM
from cm.utils import log
from cm.utils.decorators import ec2ctx_log
from cm.utils.exception import CMException

from cm.views.ec2ctx.helpers.getters import get_exposed_methods, get_submethods
from cm.views.ec2ctx.helpers.request import get_vm_by_ip
from django.conf.urls import patterns, include, url
from time import sleep
import base64
import os
import sys
import inspect

"""@package src.cm.manager.ec2ctx.latest.metadata

@copyright Copyright (c) 2013 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


@ec2ctx_log(log=True)
def ami_id(request):
    vm_ip = request.META.get('REMOTE_ADDR')
    vm = VM.get_by_ip( vm_ip )

    ami = 'ami-' + str(vm.dict['image_id'])

    return ami
ami_id.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def ami_launch_index(request):
    vm_ip = request.META.get('REMOTE_ADDR')
    vm = VM.get_by_ip( vm_ip )

    instance_id = vm.dict['vm_id']
    reservation_id = vm.long_dict['reservation_id']

    launch_index = reservation_id - instance_id + 1;

    return launch_index
ami_launch_index.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def ami_manifest_path(request):
    return 'Not implemented' # chyba nie ma odpowiednika
ami_manifest_path.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def block_device_mapping(request):
    return 'Not implemented'
block_device_mapping.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def hostname(request):
#     vm_ip = request.META.get('REMOTE_ADDR')
#
#     vm = VM.get_by_ip( vm_ip )
#
#     instance = vm.dict['name']
#     instance = instance.replace(" " , "_")
#
#
#     return instance
    return "" # TODO !!!
hostname.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def instance_action(self):
    return 'Not implemented'
instance_action.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def instance_id(request):
    vm_ip = request.META.get('REMOTE_ADDR')

    vm = VM.get_by_ip( vm_ip )

    vm_id = 'i-' + str(vm.dict['vm_id'])
    return vm_id
instance_id.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def instance_type(request):
    vm_ip = request.META.get('REMOTE_ADDR')
    vm = VM.get_by_ip( vm_ip )

    template_name = str(vm.dict['template_name'])
    return template_name
instance_type.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def kernel_id(request):
    return 'Not implemented'
kernel_id.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def local_hostname(request):
    return '' # TODO
local_hostname.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def local_ipv4(request):
    vm_ip = request.META.get('REMOTE_ADDR')
    vm = VM.get_by_ip( vm_ip )

    leases = vm.dict['leases']
    ip =  leases
    for ip in leases:
        if ip.get('address'):
            ip = ip.get('address')
        else:
            ip = ""

    return ip
local_ipv4.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def mac(request):
    return 'Not implemented'
mac.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def network(request):
    return 'Not implemented'
network.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def placement(request):
    return 'Not implemented'
placement.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def public_hostname(request):
    return '' # TODO
public_hostname.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def public_ipv4(request):
    vm_ip = request.META.get('REMOTE_ADDR')
    vm = VM.get_by_ip( vm_ip )

    leases = vm.dict['leases']
    ip =  leases
    for ip in leases:
        if ip.get('public_ip'):
            ip = ip.get('public_ip')
        else:
            ip = ""

    return ip
public_ipv4.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def public_keys(request, number=None, key_type=None):
    vm_ip = request.META.get('REMOTE_ADDR')

    vm = VM.get_by_ip( vm_ip )

    if number == "0" and vm.long_dict.get('ssh_key'):
        if key_type == "openssh-key": # HARDCODED VALUE, only one key can be assigned
            return vm.long_dict.get('ssh_key')
        else:
            if key_type:
                pass # todo error
            else:
                return "openssh-key"
    else:
        if number or key_type:
            pass # todo error

    if vm.long_dict.get('ssh_key'):
        return '0=public-key'
public_keys.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def reservation_id(request):
    vm_ip = request.META.get('REMOTE_ADDR')
    vm = VM.get_by_ip( vm_ip )

    reservation_id = vm.long_dict['reservation_id']

    return 'r-' + str(reservation_id)
reservation_id.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def security_groups(request):
    return 'default'
security_groups.func_dict['meta_data'] = True


@ec2ctx_log(log=True)
def meta_data(self):
    funcs = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    funcs = [ fun[0].replace('_','-') for fun in funcs if fun[1].func_dict.get('meta_data') ]
    return '\n'.join( funcs )

meta_data_patterns = patterns('',
                              url(r'^$', meta_data),
                              url(r'^ami-id/?$',ami_id  ),
                              url(r'^ami-manifest-path/?$', ami_manifest_path),
                              url(r'^ami-launch-index/?$', ami_launch_index),
                              url(r'^block-device-mapping/?$', block_device_mapping),
                              url(r'^hostname/?$', hostname),
                              url(r'^instance-action/?$', instance_action),
                              url(r'^instance-id/?$', instance_id),
                              url(r'^instance-type/?$', instance_type),
                              url(r'^kernel-id/?$', kernel_id),
                              url(r'^local-hostname/?$', local_hostname),
                              url(r'^local-ipv4/?$', local_ipv4),
                              url(r'^mac/?$', mac),
                              url(r'^network/?$', network),
                              url(r'^placement/?$', placement),
                              url(r'^public-hostname/?$', public_hostname),
                              url(r'^public-ipv4/?$', public_ipv4),
                              url(r'^public-keys/?$', public_keys),
                              url(r'^public-keys/(?P<number>[0-9]+)/?$', public_keys),
                              url(r'^public-keys/(?P<number>[0-9]+)/(?P<key_type>[^/]+)/?$', public_keys),
                              url(r'^reservation-id/?$', reservation_id),
                              url(r'^security-groups/?$', security_groups ))
