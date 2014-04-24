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

"""@package src.wi.forms.iso_image

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 10.06.2011
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from wi.utils import parsing
from wi.utils.forms import attrs_dict, BetterForm
from wi.utils.widgets import SelectWithDisabled


class UploadISOForm(BetterForm):
    """
    Form for <b>ISO image's ulpoad</b>.
    """
    class Meta:
        """
        Fieldset names definition.
        """
        fieldsets = (('description', {'fields': ('name', 'description'), 'legend': _('Disk description')}),
                     ('settings', {'fields': ('path', 'disk_controller'), 'legend': _('Settings')}),)

        def __init__(self):
            pass

    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_('Name'))
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512, rows=3, cols=20)),
                                  label=_('Description'))
    path = forms.CharField(widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=500, rows=3, cols=20)),
                            label=_('Link to ISO image (http:// or ftp://)'))

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(UploadISOForm, self).__init__(*args, **kwargs)

        self.fields['disk_controller'] = forms.ChoiceField(choices=parsing.parse_generic_enabled(rest_data, 'disk_controllers'),
                                                           widget=SelectWithDisabled(attrs=dict()),
                                                           label=_("Bus"))
        self.fields['disk_controller'].widget.attrs['class'] = 'medium'

    def clean_disk_controller(self):
        """
        Cast 'disk_controller' to int.
        """
        return int(self.cleaned_data['disk_controller'])


class EditISOForm(forms.Form):
    """
    Form for <b>ISO image edition</b>.
    """

    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_('ISO image name'))

    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512, rows=3, cols=20)),
                                  label=_('ISO image description'))

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(EditISOForm, self).__init__(*args, **kwargs)

        self.fields['disk_controller'] = forms.ChoiceField(choices=parsing.parse_generic_enabled(rest_data, 'disk_controllers'),
                                                           widget=SelectWithDisabled(attrs=dict()),
                                                           label=_("Bus"))
        self.fields['disk_controller'].widget.attrs['class'] = 'medium'

    def clean_disk_controller(self):
        """
        Cast 'disk_controller' to int.
        """
        return int(self.cleaned_data['disk_controller'])
