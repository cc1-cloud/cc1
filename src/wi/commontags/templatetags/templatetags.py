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

"""@package src.wi.commontags.templatetags.templatetags
@author Piotr Wójcik
@author Krzysztof Danielowski
@author Przemyslaw Syktus
@date 11.02.2010
"""
from django import template
from django.utils.translation import ugettext

register = template.Library()


@register.filter
def getitem(item, string):
    """
    Templatetag for fetching dictionary attribute values.
    """
    return item.get(string, '')


@register.filter
def filesizeformatmb(mbytes):
    """
    Function formats the [mbytes] value like a 'human-readable' file size.

    (i.e. 13 KB, 4.1 MB, 102 bytes, etc).
    """
    try:
        mbytes = float(mbytes)
    except (TypeError, ValueError, UnicodeDecodeError):
        return u"0 bytes"

    if mbytes < 1024:
        return ugettext("%d MB") % (mbytes)
    if mbytes < 1024 * 1024:
        return ugettext("%.1f GB") % (mbytes / 1024)
    if mbytes < 1024 * 1024 * 1024:
        return ugettext("%.1f TB") % (mbytes / (1024 * 1024))
    return ugettext("%.1f PB") % (mbytes / (1024 * 1024 * 1024))
filesizeformatmb.is_safe = True


class VerbatimNode(template.Node):
    """
    jQuery templates use constructs like:

        {{if condition}} print something{{/if}}

    This, of course, completely screws up Django templates,
    because Django thinks {{ and }} means something.

    Wrap {% verbatim2 %} and {% endverbatim2 %} around those
    blocks of jQuery templates and this will try its best
    to output the contents with no changes.

    This version of verbatim template tag allows you to use tags
    like url {% url 'name' %} or {% csrf_token %} within.
    """
    def __init__(self, text_and_nodes):
        self.text_and_nodes = text_and_nodes

    def render(self, context):
        output = ""

        # If its text we concatenate it, otherwise it's a node and we render it
        for bit in self.text_and_nodes:
            if isinstance(bit, basestring):
                output += bit
            else:
                output += bit.render(context)

        return output


@register.tag
def verbatim2(parser, token):
    """
    Templatetag used in workaround of the '{{' conflict between jquery templates and django templates.
    """
    text_and_nodes = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endverbatim2':
            break

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('{{')
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_TEXT:
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_BLOCK:
            try:
                command = token.contents.split()[0]
            except IndexError:
                parser.empty_block_tag(token)

            try:
                compile_func = parser.tags[command]
            except KeyError:
                parser.invalid_block_tag(token, command, None)
            try:
                node = compile_func(parser, token)
            except template.TemplateSyntaxError, ex:
                if not parser.compile_function_error(token, ex):
                    raise

            text_and_nodes.append(node)

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('}}')

    return VerbatimNode(text_and_nodes)
