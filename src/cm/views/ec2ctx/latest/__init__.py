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

from cm.models.vm import VM
from cm.utils import log
from cm.utils.decorators import ec2ctx_log
from cm.utils.exception import CMException
from cm.views.ec2ctx.helpers.request import get_vm_by_ip
from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from meta_data import meta_data, meta_data_patterns
import base64

"""@package src.cm.views.ec2ctx.latest
@copyright Copyright (c) 2013 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


@ec2ctx_log(log=True)
def user_data(request):
    vm_ip = request.META.get('REMOTE_ADDR')

    vm = VM.get_by_ip( vm_ip )
    user_data = vm.long_dict['user_data']

    return base64.b64decode( user_data )


@ec2ctx_log(log=True)
def latest(request):
    # na razie zahardkodowane, ale to sie zmieni
    return 'user-data\nmeta-data'

latest_patterns = patterns('',
                           url(r'^$', latest),
                           url(r'^meta-data/',include(meta_data_patterns) ),
                           url(r'^user-data/$', user_data) )
