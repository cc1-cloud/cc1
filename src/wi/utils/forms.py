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

"""@package src.wi.utils.forms

@author Piotr Wójcik
@date 24.03.2011
"""

from copy import deepcopy
import hashlib

from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wi.utils.regexp import regexp, regexp_text


attrs_dict = {'class': 'required'}


class RequiredSelectValidation(forms.Form):
    """
    Form checking if all values of all required selectboxes have been set.
    """
    def clean(self):
        """
        Perfoms the check.
        """
        if any([v.required and int(self.cleaned_data[k]) == -1 for k, v in self.fields.iteritems()]):
            raise forms.ValidationError(_('Please fill in all required form fields.'))
        return self.cleaned_data


class NumberChoice(object):
    """
    Used in number selection inputs.
    """
    def __init__(self, maximum=10):
        self.max_choices = maximum + 1

    def __iter__(self):
        return iter((n, n) for n in range(1, self.max_choices))


class PasswordForm(forms.Form):
    """
    Class for <b>setting password</b> form.
    """
    new_password = forms.RegexField(regex=regexp['password'],
                               max_length=255,
                               widget=forms.PasswordInput(attrs=dict(attrs_dict)),
                               label=_("Password"),
                               error_messages={'invalid': regexp_text['password']})

    password2 = forms.RegexField(regex=regexp['password'],
                                max_length=255,
                                widget=forms.PasswordInput(attrs=dict(attrs_dict)),
                                label=_("Password confirmation"),
                                error_messages={'invalid': regexp_text['password']})

    def clean(self):
        """
        Checks if given passwords match.
        """
        if 'new_password' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['new_password'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))

            self.cleaned_data['new_password'] = hashlib.sha1(self.cleaned_data['new_password']).hexdigest()
            del self.cleaned_data['password2']
        return self.cleaned_data

"""
Copyright (c) 2008, Carl J Meyer
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * The names of its contributors may not be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Time-stamp: <2008-11-21 01:54:45 carljm forms.py>

"""


class Fieldset(object):
    """
    An iterable Fieldset with a legend and a set of BoundFields.
    """
    def __init__(self, form, name, boundfields, legend=None, description=''):
        self.form = form
        self.boundfields = boundfields
        if legend is None:
            legend = name
        self.legend = mark_safe(legend)
        self.description = mark_safe(description)
        self.name = name

    def __iter__(self):
        for bfi in self.boundfields:
            yield _mark_row_attrs(bfi, self.form)

    def __repr__(self):
        return "%s('%s', %s, legend='%s', description='%s')" % (
            self.__class__.__name__, self.name,
            [f.name for f in self.boundfields], self.legend, self.description)


class FieldsetCollection(object):
    def __init__(self, form, fieldsets):
        self.form = form
        self.fieldsets = fieldsets

    def __len__(self):
        return len(self.fieldsets) or 1

    def __iter__(self):
        if not self.fieldsets:
            self.fieldsets = (('main', {'fields': self.form.fields.keys(),
                                        'legend': ''}),)
        for name, options in self.fieldsets:
            try:
                field_names = [n for n in options['fields']
                               if n in self.form.fields]
            except KeyError:
                raise ValueError("Fieldset definition must include 'fields' option.")
            boundfields = [forms.forms.BoundField(self.form, self.form.fields[n], n)
                           for n in field_names]
            yield Fieldset(self.form, name, boundfields,
                           options.get('legend', None),
                           options.get('description', ''))


def _get_meta_attr(attrs, attr, default):
    try:
        ret = getattr(attrs['Meta'], attr)
    except (KeyError, AttributeError):
        ret = default
    return ret


def get_fieldsets(bases, attrs):
    """
    Get the fieldsets definition from the inner Meta class, mapping it
    on top of the fieldsets from any base classes.

    """
    fieldsets = _get_meta_attr(attrs, 'fieldsets', ())

    new_fieldsets = {}
    order = []

    for base in bases:
        for bfs in getattr(base, 'base_fieldsets', ()):
            new_fieldsets[bfs[0]] = bfs
            order.append(bfs[0])

    for bfs in fieldsets:
        new_fieldsets[bfs[0]] = bfs
        if bfs[0] not in order:
            order.append(bfs[0])

    return [new_fieldsets[name] for name in order]


def get_row_attrs(bases, attrs):
    """
    Get the row_attrs definition from the inner Meta class.

    """
    return _get_meta_attr(attrs, 'row_attrs', {})


def _mark_row_attrs(bf, form):
    row_attrs = deepcopy(form._row_attrs.get(bf.name, {}))
    if bf.field.required:
        req_class = 'required'
    else:
        req_class = 'optional'
    if 'class' in row_attrs:
        row_attrs['class'] = row_attrs['class'] + ' ' + req_class
    else:
        row_attrs['class'] = req_class
    bf.row_attrs = mark_safe(flatatt(row_attrs))
    return bf


class BetterFormBaseMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fieldsets'] = get_fieldsets(bases, attrs)
        attrs['base_row_attrs'] = get_row_attrs(bases, attrs)
        new_class = super(BetterFormBaseMetaclass,
                          cls).__new__(cls, name, bases, attrs)
        return new_class


class BetterFormMetaclass(BetterFormBaseMetaclass, forms.forms.DeclarativeFieldsMetaclass):
    pass


class BetterModelFormMetaclass(BetterFormBaseMetaclass, forms.models.ModelFormMetaclass):
    pass


class BetterBaseForm(object):
    """
    \c BetterForm and \c BetterModelForm are subclasses of Form
    and ModelForm that allow for declarative definition of fieldsets
    and row_attrs in an inner Meta class.

    The row_attrs declaration is a dictionary mapping field names to
    dictionaries of attribute/value pairs.  The attribute/value
    dictionaries will be flattened into HTML-style attribute/values
    (i.e. {'style': 'display: none'} will become \c style="display:
    none"), and will be available as the \c row_attrs attribute of
    the \c BoundField.  Also, a CSS class of "required" or "optional"
    will automatically be added to the row_attrs of each
    \c BoundField, depending on whether the field is required.

    The fieldsets declaration is a list of two-tuples very similar to
    the \c fieldsets option on a ModelAdmin class in
    \c django.contrib.admin.

    The first item in each two-tuple is a name for the fieldset (must
    be unique, so that overriding fieldsets of superclasses works),
    and the second is a dictionary of fieldset options

    Valid fieldset options in the dictionary include:

    \c fields (required): A tuple of field names to display in this
    fieldset.

    \c classes: A list of extra CSS classes to apply to the fieldset.

    \c legend: This value, if present, will be the contents of a
    \c legend tag to open the fieldset.  If not present the unique
    name of the fieldset will be used (so a value of '' for legend
    must be used if no legend is desired.)

    \c description: A string of optional extra text to be displayed
    under the \c legend of the fieldset.

    When iterated over, the \c fieldsets attribute of a
    \c BetterForm (or \c BetterModelForm) yields \c Fieldsets.
    Each \c Fieldset has a name attribute, a legend attribute, and a
    description attribute, and when iterated over yields its
    \c BoundFields.

    For backwards compatibility, a \c BetterForm or
    \c BetterModelForm can still be iterated over directly to yield
    all of its \c BoundFields, regardless of fieldsets.

    For more detailed examples, see the doctests in tests/__init__.py.

    """
    def __init__(self, *args, **kwargs):
        self._fieldsets = deepcopy(self.base_fieldsets)
        self._row_attrs = deepcopy(self.base_row_attrs)
        super(BetterBaseForm, self).__init__(*args, **kwargs)

    @property
    def fieldsets(self):
        return FieldsetCollection(self, self._fieldsets)

    def __iter__(self):
        for bf in super(BetterBaseForm, self).__iter__():
            yield _mark_row_attrs(bf, self)


class BetterForm(BetterBaseForm, forms.Form):
    __metaclass__ = BetterFormMetaclass
    __doc__ = BetterBaseForm.__doc__


class BetterModelForm(BetterBaseForm, forms.ModelForm):
    __metaclass__ = BetterModelFormMetaclass
    __doc__ = BetterBaseForm.__doc__
