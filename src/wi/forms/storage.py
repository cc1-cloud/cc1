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

"""@package src.wi.forms.storage

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 17.10.2011
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from wi.utils import parsing
from wi.utils.forms import attrs_dict


class StorageForm(forms.Form):
    """
    Class for <b>storage's creation</b> form.
    """
    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_("Name"))
    capacity = forms.IntegerField(min_value=1,
                             label=_("Maximum capacity [MB]"),
                             help_text=_('Maximum capacity - amount of usable space'))
    address = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                               label=_("Address"),
                               help_text=_('Storage address - IP or DNS name'))
    directory = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                               label=_("Directory"),
                               help_text=_('Directory - nfs export directory'))


class MountStorageForm(forms.Form):
    """
    Class for <b>mounting storage</b> form.
    """
    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(MountStorageForm, self).__init__(*args, **kwargs)
        self.fields['storage_id'] = forms.ChoiceField(choices=parsing.parse_storage_names(rest_data),
                                                      initial=0,
                                                      label=_("Storage"))
