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

"""@package src.wi.utils.widgets

@author Piotr Wójcik
@date 20.10.2010
"""

from itertools import chain

from django.forms.widgets import Select, CheckboxSelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class SelectWithDisabled(Select):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form:
    @code
    {'label': 'option label', 'disabled': True}
    @endcode
    """
    def render_option(self, selected_choices, option_value, option_label):
        """
        """
        option_value = force_unicode(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = u' disabled="disabled"'
            option_label = option_label['label']
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(option_label)))


class CheckboxSelectMultipleWithDisabled(CheckboxSelectMultiple):
    """
    Widget adding 'disabled' option to CheckboxSelectMultiple.
    """
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul class="multipleCheckBox %s">' % (u'disabled' if len(self.choices) == 0 else u'')]

        if len(self.choices) == 0:
            output.append(u'<li><label> %s </label></li>' % (_('none available')))

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

            chb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)

            li_class = ''
            if isinstance(option_label, dict):
                if dict.get(option_label, 'disabled'):
                    chb.attrs['disabled'] = 'disabled'
                    li_class = 'disabled'
                option_label = option_label['label']

            option_value = force_unicode(option_value)
            rendered_cb = chb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li class="%s"><label%s>%s %s</label></li>' % (li_class, label_for, rendered_cb, option_label))

        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))
