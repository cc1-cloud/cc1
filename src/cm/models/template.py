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

"""@package src.cm.models.template

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <di.dijo@gmail.com>
"""

from django.db import models

from cm.utils.exception import CMException
from common.states import template_states


class Template(models.Model):
    """
    @model{TEMPLATE} Class for virtual machine templates

    Template is what defines virtual hardware params: CPU and memory.
    Each template specifies amount of points consumed from user's quota
    per hour. Template is described by its name and description.
    """
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=512)
    memory = models.IntegerField()
    cpu = models.IntegerField()
    template_states = (
        (0, 'active'),
        (1, 'deleted')
    )
    state = models.IntegerField(choices=template_states)
    points = models.IntegerField()
    ec2name = models.IntegerField(default=0)

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return self.name

    @property
    def dict(self):
        """
        @returns{dict} this Template's data
        \n fields:
        @dictkey{id,int}
        @dictkey{name,string} human-readable this Template's name displayed in web-interface
        @dictkey{cpu,int} Number of CPUs for VM started from this Template
        @dictkey{memory,int} amount of memory [MB] booked by VM started from this Template
        @dictkey{points,int} amount of points consumed by this VM
        @dictkey{description,string} human-readable description of this Template
        @dictkey{ec2name,string} Template's name for EC2 interface
        """
        d = {}
        d['template_id'] = self.id
        d['name'] = self.name
        d['cpu'] = self.cpu
        d['memory'] = self.memory
        d['points'] = self.points
        d['description'] = self.description
        d['ec2name'] = self.ec2name
        # state is not put in dictionary
        return d

    @staticmethod
    def get(template_id):
        """
        @parameter{template_id,int} id of the requested Template

        @returns{Template} instance of requested Template

        @raises{template_get,CMException} requested Template doesn't exist
        or it's state isn't active
        """
        try:
            template = Template.objects.get(pk=template_id)
        except:
            raise CMException('template_get')

        if not template or template.state != template_states['active']:
            raise CMException('template_get')

        return template
