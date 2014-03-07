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

"""@package src.wi.forms.farm

@author Piotr Wójcik
@date 14.11.2011
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from wi.forms.vm import EditVMForm
from wi.utils import parsing
from wi.utils.forms import NumberChoice
from wi.utils.views import make_request
from wi.utils.widgets import SelectWithDisabled, \
    CheckboxSelectMultipleWithDisabled


class CreateFarmForm1(forms.Form):
    """
    First step of form for <b>creating a farm</b>.
    """
    image_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CreateFarmForm1, self).__init__(*args, **kwargs)

    def clean_image_id(self):
        """
        Cast 'image_id' to int.
        """
        if int(self.cleaned_data['image_id']) < 0:
            raise forms.ValidationError(_("Please select an image."))
        else:
            return int(self.cleaned_data['image_id'])


class CreateFarmForm2(forms.Form):
    """
    Second step of form for <b>creating a farm</b>.
    """
    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        self.session = kwargs.pop('session')
        super(CreateFarmForm2, self).__init__(*args, **kwargs)

        self.fields['head_template_id'] = forms.ChoiceField(choices=parsing.parse_template_names(rest_data),
                                                          initial=0,
                                                          widget=SelectWithDisabled(attrs=dict()),
                                                          label=_('Head template'))

        self.fields['worker_template_id'] = forms.ChoiceField(choices=parsing.parse_template_names(rest_data),
                                                              initial=0,
                                                              widget=SelectWithDisabled(attrs=dict()),
                                                              label=_('Worker node template'),
                                                              help_text=_('Template of worker nodes - worker nodes parameters'))

        self.fields['count'] = forms.ChoiceField(choices=NumberChoice(24),
                                                 initial=0,
                                                 widget=forms.Select(attrs=dict({'class': 'xsmall'})),
                                                 label=_('Number of worker nodes'),
                                                 help_text=_('Number of worker nodes - (other than head)'))

    def clean_head_template_id(self):
        """
        Cast 'head_template_id' to int.
        """
        if int(self.cleaned_data['head_template_id']) < 0:
            raise forms.ValidationError(_("Please select a template."))
        else:
            return int(self.cleaned_data['head_template_id'])

    def clean_worker_template_id(self):
        """
        Cast 'worker_template_id' to int.
        """
        if int(self.cleaned_data['worker_template_id']) < 0:
            raise forms.ValidationError(_("Please select a template."))
        else:
            return int(self.cleaned_data['worker_template_id'])

    def clean_count(self):
        """
        Cast 'count' to int.
        """
        return int(self.cleaned_data['count'])

    def clean(self):
        """
        Checks if there is enough space on CM.
        """
        if not self.cleaned_data.get('count') or not self.cleaned_data.get('worker_template_id') or not self.cleaned_data.get('head_template_id'):
            return None

        response = make_request('user/farm/check_resources/',
                                {'count': self.cleaned_data.get('count'),
                                 'template_id': self.cleaned_data.get('worker_template_id'),
                                 'head_template_id': self.cleaned_data.get('head_template_id')
                                 }, user=self.session['user'])

        if response['status'] == 'ok' and response['data'] == False:
            raise forms.ValidationError(_("Not enough resources. Choose smaller farm or try again later."))
        else:
            return self.cleaned_data


class CreateFarmForm3(forms.Form):
    """
    Third step of form for <b>creating a farm</b>.
    """
    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(CreateFarmForm3, self).__init__(*args, **kwargs)

        self.fields['public_ip_id'] = forms.ChoiceField(choices=parsing.parse_ips(rest_data),
                                               required=False,
                                               widget=SelectWithDisabled(attrs=dict()),
                                               label=_('Assign IP address'),
                                               help_text=_('Public IP address - To request new IP address go to: VM Resources -&gt; Elastic IP addresses'))

        self.fields['disk_list'] = forms.MultipleChoiceField(choices=parsing.parse_disks(rest_data, False),
                                                           required=False,
                                                           widget=CheckboxSelectMultipleWithDisabled,
                                                           label=_('Attach disk volume'),
                                                           help_text=_('Virtual disk - '))

        self.fields['iso_list'] = forms.ChoiceField(choices=parsing.parse_iso(rest_data),
                                                   required=False,
                                                   widget=SelectWithDisabled(attrs=dict()),
                                                   label=_("Attach ISO image"))

        self.fields['vnc'] = forms.BooleanField(required=False,
                                              label=_('VNC'),
                                              widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
                                              help_text=_('VNC - Enable/Disable VNC redirection'))

        self.fields.keyOrder = ['public_ip_id', 'disk_list', 'iso_list', 'vnc']

    def clean_public_ip_id(self):
        """
        Cast 'public_ip_id' to int.
        """
        return int(self.cleaned_data['public_ip_id'])

    def clean_disk_list(self):
        """
        Cast each item in 'dist_list' to int.
        """
        for i in self.cleaned_data['disk_list']:
            if int(i) < 0:
                return []
        return [int(a) for a in self.cleaned_data['disk_list']]

    def clean_iso_list(self):
        """
        Cast each item in 'iso_list' to int.
        """
        if int(self.cleaned_data['iso_list']) < 0:
            return []
        return [int(self.cleaned_data['iso_list'])]


class CreateFarmForm4(EditVMForm):
    """
    Final step of form for <b>creating a farm</b>.
    """
    def __init__(self, *args, **kwargs):
        super(CreateFarmForm4, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['name', 'description']
