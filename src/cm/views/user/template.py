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

"""@package src.cm.views.user.template
@alldecoratedby{src.cm.utils.decorators.user_log}

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""
from cm.models.template import Template
from cm.utils.exception import CMException
from common.states import template_states
from cm.utils.decorators import user_log


@user_log(log=True)
def get_list(caller_id):
    """
    Method returns list of templates.
    @cmview_user

    @response{list(dict)} dicts describing templates
    """
    try:
        templates = [t.dict for t in Template.objects.filter(state__exact=template_states['active']).order_by('cpu', 'memory')]
    except:
        raise CMException("template_list")

    return templates


@user_log(log=True)
def get_by_id(caller_id, template_id):
    """
    @cmview_user

    @parameter{template_id,int}

    @response{dict} template data
    """
    try:
        t = Template.objects.get(id=template_id)
    except:
        raise CMException("template_get")

    return t.dict

