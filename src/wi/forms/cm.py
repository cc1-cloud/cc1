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

"""@package src.wi.forms.cm

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.12.2010
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from wi.utils.forms import PasswordForm, attrs_dict
from wi.utils.regexp import regexp, regexp_text


class EditCMForm(forms.Form):
    """
    Class for <b>CM edition</b> form.
    """

    name = forms.RegexField(regex=regexp['dev_name'],
                            max_length=40,
                            label=_("Name"),
                            widget=forms.TextInput(attrs=attrs_dict),
                            error_messages={'invalid': regexp_text['dev_name']})
    address = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                              label=_("Address"))
    port = forms.IntegerField(label=_("Port"))


class CreateCMForm(EditCMForm, PasswordForm):
    """
    Class for <b>CM creation</b> form.
    """
