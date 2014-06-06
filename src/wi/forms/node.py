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

"""@package src.wi.forms.node

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 17.10.2011
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from wi.utils import parsing
from wi.utils.forms import attrs_dict, BetterForm


class MountNodeForm(forms.Form):
    """
    Class for <b>mounting node</b> form.
    """
    def __init__(self, *args, **kwargs):
        rest_data = kwargs.pop('rest_data')
        super(MountNodeForm, self).__init__(*args, **kwargs)
        self.fields['node_id'] = forms.ChoiceField(choices=parsing.parse_node_names(rest_data),
                                                   initial=0,
                                                   label=_("Node"))


class NodeForm(BetterForm):
    """
    Class for <b>creating a node</b> form.
    """

    class Meta:
        """
        Fieldset names definition.
        """
        fieldsets = (('libvirt', {'fields': ('address',), 'legend': _('Libvirt configuration')}),
                     ('resources', {'fields': ('hdd_total', 'cpu_total', 'memory_total'), 'legend': _('Node capacity')}),)

        def __init__(self):
            pass

    def __init__(self, *args, **kwargs):
        super(NodeForm, self).__init__(*args, **kwargs)


        self.fields['address'] = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=45)),
                                                 label=_('Node address'),
                                                 help_text=_('Node address - IP or DNS name'))
        self.fields['hdd_total'] = forms.IntegerField(min_value=1,
                                                      label=_('HDD Total [MB]'),
                                                      help_text=_(' - total amount of storage for virtual machine images'))
        self.fields['cpu_total'] = forms.IntegerField(min_value=1,
                                                      label=_('Cpu Total'),
                                                      help_text=_(' - total amount of CPU\'s for libvirt'))
        self.fields['memory_total'] = forms.IntegerField(min_value=1,
                                                         label=_('Memory Total [MB]'),
                                                         help_text=_(' - total amount of RAM'))


class EditNodeForm(NodeForm, BetterForm):
    """
    Class for <b>editing a node</b> form.
    """

    class Meta:
        """
        Fieldset names definition.
        """
        fieldsets = (('libvirt', {'fields': ('address', 'comment'), 'legend': _('Libvirt configuration')}),
                     ('resources', {'fields': ('hdd_total', 'cpu_total', 'memory_total'), 'legend': _('Node capacity')}),)

        def __init__(self):
            pass

    def __init__(self, *args, **kwargs):
            super(EditNodeForm, self).__init__(*args, **kwargs)
            self.fields['comment'] = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs=dict(attrs_dict,
                                                                   maxlength=256,
                                                                   rows=4, cols=20)),
                                  label=_('Comment'))
