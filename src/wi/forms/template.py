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

"""@package src.wi.forms.template

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 17.10.2011
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from wi.utils.forms import attrs_dict
from wi.utils.states import ec2names_reversed


class TemplateForm(forms.Form):
    """
    Class for <b>template creation</b> form.
    """
    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_("Name"))
    cpu = forms.IntegerField(min_value=1,
                             initial=1,
                             label=_("Cpu"))
    memory = forms.IntegerField(min_value=64,
                                initial=2048,
                                label=_("Memory [MB]"))
    points = forms.IntegerField(max_value=1000000,
                                min_value=1,
                                label=_("Points per hour"))
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512, rows=3, cols=20)),
                                  label=_("Description"))

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.fields['ec2name'] = forms.ChoiceField(choices=ec2names_reversed.items(),
                                                   label=_('Ec2 name'))
        self.fields['ec2name'].widget.attrs['class'] = 'large'
        self.fields.keyOrder = ['name', 'ec2name', 'cpu', 'memory', 'points', 'description']

    def clean_ec2name(self):
        """
        Cast 'ec2name' to int.
        """
        return int(self.cleaned_data['ec2name'])
