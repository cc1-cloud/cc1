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

"""@package src.wi.forms.public_ip

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 17.10.2011
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from wi.utils.forms import attrs_dict


class AddPublicIPForm(forms.Form):
    """
    Form for **public ip creation**.
    """
    start_address = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                                                 label=_('First IP address'))
    count = forms.IntegerField(min_value=1, initial=1,
                               label=_('Number of IP'))
