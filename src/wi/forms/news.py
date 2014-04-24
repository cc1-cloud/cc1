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

"""@package src.wi.forms.news

@author Krzysztof Danielowski
@author Piotr Wojcik
@date 17.03.2011
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from wi.utils.forms import attrs_dict


class NewsForm(forms.Form):
    """
    Form for <b>news' creation</b>.
    """
    topic = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=255)),
                            label=_('Topic'))
    content = forms.CharField(widget=forms.Textarea(attrs=dict(attrs_dict, maxlength=512)),
                              label=_('Content'),
                              help_text=_('News content - may include Markdown markup language, e.g., *text* for italics, **text** for bold text, * item for unordered list, 1. item for ordered list, [link name](http://address) for anchor, `code` for preformated code.'))
    sticky = forms.BooleanField(required=False,
                                label=_('Important'),
                                widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
                                help_text=_('Important news - will appear on the main page'))
