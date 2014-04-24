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

"""@package src.wi.forms.group

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.12.2010
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from wi.utils.forms import attrs_dict


class GroupForm(forms.Form):
    """
    Class for <b>group creation/edition</b> form.
    """
    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_("Name"))
    description = forms.CharField(required=False,
                           widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512, rows=3, cols=20)),
                           label=_("Description"))
