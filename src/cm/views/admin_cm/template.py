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

"""@package src.cm.views.admin_cm.template

@alldecoratedby{src.cm.utils.decorators.admin_cm_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""
from cm.models.template import Template
from cm.utils.exception import CMException
from common.states import template_states
from cm.utils.decorators import admin_cm_log


@admin_cm_log(log=False)
def get_list(caller_id):
    """
    Returns list of Templates.

    @cmview_admin_cm
    @response{list(dict)} Template.dict property of each Template
    """

    try:
        templates = [t.dict for t in Template.objects.filter(state__exact=template_states['active']).order_by('cpu', 'memory')]
    except:
        raise CMException("template_list")

    return templates


@admin_cm_log(log=True)
def get_by_id(caller_id, template_id):
    """
    @cmview_admin_cm
    @param_post{template_id,int}

    @response{dict} Template.dict property of the requested Template
    """

    try:
        t = Template.objects.get(id=template_id)

    except:
        raise CMException("template_get")

    return t.dict


@admin_cm_log(log=True)
def add(caller_id, name, memory, cpu, description, points, ec2name):
    """
    Creates and saves new VM Template.

    @cmview_admin_cm
    @param_post{name,string}
    @param_post{memory,int}
    @param_post{cpu,int}
    @param_post{description,string}
    @param_post{points,int}
    @param_post{ec2name,string} name for EC2 interface
    """

    try:
        template = Template()
        template.name = name
        template.memory = memory
        template.cpu = cpu
        template.description = description
        template.points = points
        template.ec2name = ec2name
        template.state = template_states['active']
        template.save()

    except:
        raise CMException('template_create')


@admin_cm_log(log=True)
def delete(caller_id, template_id):
    """
    Sets specified Template's state as @val{deleted}.

    @cmview_admin_cm
    @param_post{template_id,int} id of the Template to remove.
    """

    try:
        template = Template.objects.get(pk=template_id)
        template.state = template_states['deleted']
        template.save()
    except:
        raise CMException('template_delete')


@admin_cm_log(log=True)
def edit(caller_id, template_id, name, memory, cpu, description, points, ec2name):
    """
    Updates specified Template's attributes.

    @cmview_admin_cm
    @param_post{template_id,int} id of the Template to edit
    @param_post{name,string}
    @param_post{memory,int}
    @param_post{cpu,int}
    @param_post{description,string}
    @param_post{points,int}
    @param_post{ec2name,int}
    """

    try:
        template = Template.objects.get(pk=template_id)
        template.name = name
        template.memory = memory
        template.cpu = cpu
        template.description = description
        template.points = points
        template.ec2name = ec2name
        template.save()
    except:
        raise CMException('template_edit')
