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
    Method returns list of templates.
    @cmview_admin_cm

    @parameter{caller_id,int}

    @response{list(dict)} dicts describing templates
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

    @parameter{caller_id,int}
    @parameter{template_id,int}

    @response{dict} information about template
    """

    try:
        t = Template.objects.get(id=template_id)

    except:
        raise CMException("template_get")

    return t.dict


@admin_cm_log(log=True)
def add(caller_id, name, memory, cpu, description, points, ec2name):
    """
    Create new template instance and add it to db.
    @cmview_admin_cm

    @dictkey{name,string}
    @dictkey{memory,int}
    @dictkey{cpu,int}
    @dictkey{description,string}
    @dictkey{points,int}
    @dictkey{ec2name,string}

    @response{None}
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
    Method deletes templates with given \c template_id.
    @cmview_admin_cm

    @parameter{caller_id,int}
    @parameter{template_id,int} managed template's id

    @response{None}
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
    Function edits template id as described by params in \c request and inserts it to database.
    @cmview_admin_cm

    @parameter{caller_id,int}
    @parameter{template_id,int} managed template's id
    @parameter{name,string}
    @parameter{memory,int}
    @parameter{cpu,int}
    @parameter{description,string}
    @parameter{points,int}
    @parameter{ec2name,int}

    @response{None}
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
