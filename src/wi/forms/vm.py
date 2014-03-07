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

"""@package src.wi.forms.vm

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 26.11.2010
"""

from itertools import chain

from django import forms
from django.forms.fields import CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wi.utils import parsing
from wi.utils.forms import attrs_dict, RequiredSelectValidation
from wi.utils.regexp import regexp, regexp_text
from wi.utils.states import stat_names_reversed, stat_short_names_reversed, \
    stat_resolutions_reversed, stat_ranges_reversed
from wi.utils.widgets import SelectWithDisabled, \
    CheckboxSelectMultipleWithDisabled


class My2CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li class="stats ' + stat_short_names_reversed[int(option_value)] + '"><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


class EditVMForm(forms.Form):
    """
    Form for <b>VM edition</b>.
    """

    name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                           label=_('Name'))
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512, rows=4, cols=20)),
                                  label=_('Description'))


class SetSshKeyForm(forms.Form):
    """
    Form for <b>setting SSH key</b>.
    """

    vm_username = forms.RegexField(regex=regexp['login'],
                                   initial="root",
                                   widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=35)),
                                   error_messages={'invalid': regexp_text['login']},
                                   label=_('Username'))

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(SetSshKeyForm, self).__init__(*args, **kwargs)
        self.fields['vm_key'] = forms.ChoiceField(choices=parsing.parse_ssh_keys(rest_data), initial=0, label=_('Key'))
        self.fields['vm_key'].widget.attrs['class'] = 'medium'

    def clean_vm_key(self):
        """
        Cast 'vm_key' to int.
        """
        return int(self.cleaned_data['vm_key'])


class ChangeVMPasswordForm(forms.Form):
    """
    Form for <b>changing VM password</b>.
    """

    vm_username = forms.RegexField(regex=regexp['login'],
                                   initial="root",
                                   widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=35)),
                                   error_messages={'invalid': regexp_text['login']},
                                   label=_('Username'))


class AssignChosenIPForm(RequiredSelectValidation):
    """
    Form for <b>IP assignment</b>.
    """

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(AssignChosenIPForm, self).__init__(*args, **kwargs)
        self.fields['public_ip_id'] = forms.ChoiceField(choices=parsing.parse_ips(rest_data, False), initial=0,
                                              widget=SelectWithDisabled(attrs=dict({'class': 'medium'})),
                                              label=_("IP address"))
        self.fields['public_ip_id'].widget.attrs['class'] = 'medium'

    def clean_public_ip_id(self):
        """
        Cast 'public_ip_id' to int.
        """
        return int(self.cleaned_data['public_ip_id'])


class AssignIPForm(RequiredSelectValidation):
    """
    Form for <b>IP assignment</b>.
    """

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(AssignIPForm, self).__init__(*args, **kwargs)
        self.fields['public_ip_id'] = forms.ChoiceField(choices=parsing.parse_ips(rest_data, False), initial=0,
                                              widget=SelectWithDisabled(attrs=dict({'class': 'medium'})),
                                              label=_("IP address"))
        self.fields['public_ip_id'].widget.attrs['class'] = 'medium'
        self.fields['lease_id'] = forms.ChoiceField(choices=parsing.parse_leases(rest_data), initial=0,
                                              widget=SelectWithDisabled(attrs=dict({'class': 'medium'})),
                                              label=_("Lease"))
        self.fields['lease_id'].widget.attrs['class'] = 'medium'

    def clean_lease_id(self):
        """
        Cast 'lease_id' to int.
        """
        return int(self.cleaned_data['lease_id'])

    def clean_public_ip_id(self):
        """
        Cast 'public_ip_id' to int.
        """
        return int(self.cleaned_data['public_ip_id'])


class RevokeIPForm(RequiredSelectValidation):
    """
    For for IP address revoking.
    """

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(RevokeIPForm, self).__init__(*args, **kwargs)
        self.fields['public_ip_id'] = forms.ChoiceField(choices=parsing.parse_ips_from_vm(rest_data), initial=0,
                                              widget=SelectWithDisabled(attrs=dict({'class': 'medium'})),
                                              label=_("IP address"))
        self.fields['public_ip_id'].widget.attrs['class'] = 'medium'

    def clean_public_ip_id(self):
        """
        Cast 'public_ip_id' to int.
        """
        return int(self.cleaned_data['public_ip_id'])


class AssignDiskForm(RequiredSelectValidation):
    """
    Form for <b>disk assignment</b>.
    """

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(AssignDiskForm, self).__init__(*args, **kwargs)
        self.fields['storage_image_id'] = forms.ChoiceField(choices=parsing.parse_disks(rest_data, False), initial=0,
                                                  widget=SelectWithDisabled(attrs=dict({'class': 'medium'})),
                                                  label=_("Disk"))
        self.fields['storage_image_id'].widget.attrs['class'] = 'medium'

    def clean_storage_image_id(self):
        """
        Cast 'storage_image_id' to int.
        """
        return int(self.cleaned_data['storage_image_id'])


class RevokeDiskForm(RequiredSelectValidation):
    """
    Form for <b>disk unassignment</b>.
    """

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(RevokeDiskForm, self).__init__(*args, **kwargs)
        self.fields['storage_image_id'] = forms.ChoiceField(choices=parsing.parse_disks_from_vm(rest_data), initial=0,
                                                  widget=SelectWithDisabled(attrs=dict({'class': 'medium'})),
                                                  label=_('Disk'))
        self.fields['storage_image_id'].widget.attrs['class'] = 'medium'

    def clean_storage_image_id(self):
        """
        Cast 'img_id' to int.
        """
        return int(self.cleaned_data['storage_image_id'])


class CreateVMForm1(forms.Form):
    """
    Form for <b>creating a virtual machine</b>.
    """

    image_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CreateVMForm1, self).__init__(*args, **kwargs)

    def clean_image_id(self):
        """
        Cast 'image_id' to int.
        """
        if int(self.cleaned_data['image_id']) < 0:
            raise forms.ValidationError(_('Please select an image.'))
        else:
            return int(self.cleaned_data['image_id'])


class CreateVMForm2(forms.Form):
    """
    Form for <b>creating a virtual machine</b>.
    """

    template_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CreateVMForm2, self).__init__(*args, **kwargs)

    def clean_template_id(self):
        """
        Cast 'template_id' to int.
        """
        if int(self.cleaned_data['template_id']) < 0:
            raise forms.ValidationError(_('Please select a template.'))
        else:
            return int(self.cleaned_data['template_id'])


class CreateVMForm3(forms.Form):
    """
    Form for <b>creating a virtual machine</b>.
    """

    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(CreateVMForm3, self).__init__(*args, **kwargs)

        self.fields['public_ip_id'] = forms.ChoiceField(choices=parsing.parse_ips(rest_data),
                                                 required=False,
                                                 widget=SelectWithDisabled(attrs=dict()),
                                                 label=_('Assign IP address'),
                                                 help_text=_('Public IP address - To get a new IP address go to: VM Resources -&gt; Elastic IP addresses'))

        self.fields['disk_list'] = forms.MultipleChoiceField(choices=parsing.parse_disks(rest_data, True),
                                                            required=False,
                                                            widget=CheckboxSelectMultipleWithDisabled,
                                                            label=_('Attach disk volume'),
                                                            help_text=_('Virtual disk - '))

        self.fields['iso_list'] = forms.ChoiceField(choices=parsing.parse_iso(rest_data),
                                                   required=False,
                                                   widget=SelectWithDisabled(attrs=dict()),
                                                   label=_("Attach ISO image"))

        self.fields['vnc'] = forms.BooleanField(required=False,
                                                label=_("VNC"),
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
        Cast each item in 'disk_list' to int.
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


class CreateVMForm4(EditVMForm):
    """
    Form for <b>creating a virtual machine</b>.
    """

    def __init__(self, *args, **kwargs):
        super(CreateVMForm4, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['name', 'description']


class MonitoringVMForm(forms.Form):
    """
    Form for fetching the monitoring data for a selected virtual machine.
    """

    vm_id = forms.CharField(widget=forms.HiddenInput())
    time = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(MonitoringVMForm, self).__init__(*args, **kwargs)

        self.fields['stat_name'] = forms.MultipleChoiceField(choices=stat_names_reversed.items(),
                                                            widget=My2CheckboxSelectMultiple,
                                                            label=_('Statistic'),
                                                            initial=['0'])
        self.fields['resolution'] = forms.ChoiceField(choices=stat_resolutions_reversed.items(),
                                                      label=_('Time range'))
        self.fields['resolution'].widget.attrs['class'] = 'small'

        self.fields['stat_range'] = forms.ChoiceField(choices=stat_ranges_reversed.items(),
                                                 label=_('Period'))
        self.fields['stat_range'].widget.attrs['class'] = 'small'

    def clean_vm_id(self):
        """
        Cast 'vm_id' to int.
        """
        return int(self.cleaned_data['vm_id'])

    def clean_stat_name(self):
        """
        Cast 'stat_name' to int.
        """
        return [int(i) for i in self.cleaned_data['stat_name']]

    def clean_resolution(self):
        """
        Cast 'resolution' to int.
        """
        return int(self.cleaned_data['resolution'])

    def clean_stat_range(self):
        """
        Cast 'stat_range' to int.
        """
        return int(self.cleaned_data['stat_range'])


class CreateVMOnNodeForm(EditVMForm, CreateVMForm3):
    """
    CM admin's form for <b>creating a virtual machine</b>.
    """

    def __init__(self, *args, **kwargs):
        # not .pop() because CreateVMForm3 also needs it
        rest_data = kwargs['rest_data']
        super(CreateVMOnNodeForm, self).__init__(*args, **kwargs)

        self.fields['image_id'] = forms.ChoiceField(choices=parsing.parse_image_names(rest_data),
                                                  widget=SelectWithDisabled(attrs=dict()),
                                                  label=_("Image"),
                                                  help_text=_('Image file - From your public, private or group image pool'))

        self.fields['template_id'] = forms.ChoiceField(choices=parsing.parse_template_names(rest_data),
                                                     widget=forms.Select(attrs=dict()),
                                                     label=_("Template"),
                                                     help_text=_('Template of machine - Virtual machine parameters'))

        self.fields.keyOrder = ['image_id', 'name', 'description',
                                'template_id', 'public_ip_id', 'disk_list',
                                'iso_list', 'vnc']

    def clean_image_id(self):
        """
        Cast 'image_id' to int.
        """
        if int(self.cleaned_data['image_id']) < 0:
            raise forms.ValidationError(_("Please select an image."))
        else:
            return int(self.cleaned_data['image_id'])

    def clean_template_id(self):
        """
        Cast 'template_id' to int.
        """
        if int(self.cleaned_data['template_id']) < 0:
            raise forms.ValidationError(_("Please select a template."))
        else:
            return int(self.cleaned_data['template_id'])
