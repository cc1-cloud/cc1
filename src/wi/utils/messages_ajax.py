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

"""@package src.wi.utils.messages_ajax

@author Piotr Wójcik
@date 23.11.2010
"""

import json

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from wi.utils.exceptions import RestErrorException


def success(message, status=0):
    """
    Returns json encoded ajax response.
    """
    return HttpResponse(content=json.dumps({'status': status, 'data': message}), content_type="application/json")


def error(message):
    """
    Returns json encoded ajax response (error).
    """
    return success(message, status=8000)


def success_with_key(message, filename, name, status=0):
    """
    Returns json encoded ajax response containing a file.
    """
    return HttpResponse(content=json.dumps({'status': status, 'data': message, 'file': filename, 'name': name}), content_type="application/json")


def ajax_request(view_func):
    """
    Decorator checking whether request is an AJAX request.
    """
    def wrap(request, *args, **kwds):
        """
        Returned decorated function.
        """
        if not request.is_ajax():
            return error(_('Not AJAX request!'))
        try:
            return view_func(request, *args, **kwds)
        except RestErrorException as ex:
            return error(ex.value)
    return wrap
