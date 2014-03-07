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

"""@package src.wi.forms.storage_image

@author Krzysztof Danielowski
@author Piotr Wójcik
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from wi.utils import parsing
from wi.utils.forms import attrs_dict, BetterForm
from wi.utils.states import image_platforms_reversed
from wi.utils.widgets import SelectWithDisabled


class EditDiskForm(forms.Form):
    """
    Form for <b>disk edition</b>.
    """

    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_('Disk name'))

    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512, rows=3, cols=20)),
                                  label=_('Disk description'))

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(EditDiskForm, self).__init__(*args, **kwargs)

        self.fields['disk_controller'] = forms.ChoiceField(choices=parsing.parse_generic_enabled(rest_data, 'disk_controllers'),
                                                           widget=SelectWithDisabled(attrs=dict()),
                                                           label=_("Bus"))
        self.fields['disk_controller'].widget.attrs['class'] = 'medium'

    def clean_disk_controller(self):
        """
        Cast 'disk_controller' to int.
        """
        return int(self.cleaned_data['disk_controller'])


class AddDiskForm(EditDiskForm):
    """
    Form for <b>disk addition</b>.
    """
    size = forms.IntegerField(max_value=2000000,
                              min_value=1,
                              label=_('Disk size [MB]'))

    def __init__(self, *args, **kwargs):
        super(AddDiskForm, self).__init__(*args, **kwargs)
        rest_data = kwargs.pop('rest_data')

        self.fields['filesystem'] = forms.ChoiceField(choices=parsing.parse_generic(rest_data, 'supported_filesystems'),
                                                           widget=SelectWithDisabled(attrs=dict()),
                                                           label=_('File system'))
        self.fields['filesystem'].widget.attrs['class'] = 'medium'

    def clean_filesystem(self):
        """
        Cast 'filesystem' to int.
        """
        return int(self.cleaned_data['filesystem'])


class UploadDiskForm(BetterForm):
    """
    Form for <b>disk's ulpoad</b>.
    """
    class Meta:
        """
        Fieldset names definition.
        """
        fieldsets = (('description', {'fields': ('name', 'description'), 'legend': _('Disk description')}),
                     ('settings', {'fields': ('path', 'disk_controller', 'filesystem'), 'legend': _('Settings')}),)

        def __init__(self):
            pass

    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_('Name'))
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512, rows=3, cols=20)),
                                  label=_('Description'))
    path = forms.CharField(widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=500, rows=3, cols=20)),
                            label=_('Link to disk (http:// or ftp://)'))

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(UploadDiskForm, self).__init__(*args, **kwargs)

        self.fields['disk_controller'] = forms.ChoiceField(choices=parsing.parse_generic_enabled(rest_data, 'disk_controllers'),
                                                           widget=SelectWithDisabled(attrs=dict()),
                                                           label=_("Bus"))
        self.fields['disk_controller'].widget.attrs['class'] = 'medium'

    def clean_disk_controller(self):
        """
        Cast 'disk_controller' to int.
        """
        return int(self.cleaned_data['disk_controller'])


class ConvertImageForm(forms.Form):
    """
    Form for <b>adding HTTP to image</b>.
    """

    platform = forms.ChoiceField(choices=image_platforms_reversed.items(),
                                                    label=_('Platform'))

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(ConvertImageForm, self).__init__(*args, **kwargs)
        self.fields['platform'].widget.attrs['class'] = 'medium'

        self.fields['disk_controller'] = forms.ChoiceField(choices=parsing.parse_generic_enabled(rest_data, 'disk_controllers'),
                                                           widget=SelectWithDisabled(attrs=dict()),
                                                           label=_('Bus'))
        self.fields['disk_controller'].widget.attrs['class'] = 'medium'

        self.fields['video_device'] = forms.ChoiceField(choices=parsing.parse_generic(rest_data, 'video_devices'),
                                                        widget=SelectWithDisabled(attrs=dict()),
                                                        label=_('Video'))
        self.fields['video_device'].widget.attrs['class'] = 'medium'

        self.fields['network_device'] = forms.ChoiceField(choices=parsing.parse_generic(rest_data, 'network_devices'),
                                                          widget=SelectWithDisabled(attrs=dict()),
                                                          label=_("Net"))
        self.fields['network_device'].widget.attrs['class'] = 'medium'

    def clean_disk_controller(self):
        """
        Cast 'disk_controller' to int.
        """
        return int(self.cleaned_data['disk_controller'])

    def clean_video_device(self):
        """
        Cast 'video_device' to int.
        """
        return int(self.cleaned_data['video_device'])

    def clean_network_device(self):
        """
        Cast 'network_device' to int.
        """
        return int(self.cleaned_data['network_device'])

    def clean_platform(self):
        """
        Cast 'platform' to int.
        """
        return int(self.cleaned_data['platform'])
