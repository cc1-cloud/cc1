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

"""@package src.wi.utils.decorators

@author Piotr Wójcik
@author Krzysztof Danielowski
"""

import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import urlquote

from wi.utils import REDIRECT_FIELD_NAME
from wi.utils.errors import auth_error_text
from wi.utils.messages_ajax import success


def django_view(fun):
    """
    Logs any exception thrown by a view.
    """
    wi_logger = logging.getLogger('wi_logger')

    def wrapper(*args, **kwargs):
        """
        Returned decorated function.
        """
        try:
            ret = fun(*args, **kwargs)
        except Exception, ex:
            wi_logger.exception('General exception: %s' % str(ex))
            raise ex
        return ret
    wrapper.__module__ = fun.__module__
    wrapper.__name__ = fun.__name__
    wrapper.__doc__ = fun.__doc__
    return wrapper

login_url = settings.LOGIN_URL
cm_login_url = '/admin_cm/login/'


def user_permission(view_func):
    """
    \b Decorator for views with logged user permissions.
    """
    def wrap(request, *args, **kwds):
        """
        Returned decorated function.
        """
        if 'user' in request.session:
            return view_func(request, *args, **kwds)
        if request.is_ajax():
            return success(unicode(auth_error_text), status=8002)
        path = urlquote(request.get_full_path())
        tup = login_url, REDIRECT_FIELD_NAME, path
        return HttpResponseRedirect('%s?%s=%s' % tup)
    return wrap


def admin_clm_permission(view_func):
    """
    \b Decorator for views with logged Cloud Manager admin permissions.
    """
    def wrap(request, *args, **kwds):
        """
        Returned decorated function.
        """
        if 'user' in request.session and request.session['user'].is_admin_clm:
            return view_func(request, *args, **kwds)
        if request.is_ajax():
            return success(auth_error_text, status=8003)
        path = urlquote(request.get_full_path())
        tup = login_url, REDIRECT_FIELD_NAME, path
        return HttpResponseRedirect('%s?%s=%s' % tup)
    return wrap


def admin_cm_permission(view_func):
    """
    \b Decorator for views with logged Cluster Manager admin permissions.
    """
    def wrap(request, *args, **kwds):
        """
        Returned decorated function.
        """
        if 'user' in request.session and request.session['user'].is_admin_cm:
            return view_func(request, *args, **kwds)
        if request.is_ajax():
            return success(auth_error_text, status=8004)
        path = urlquote(request.get_full_path())
        tup = cm_login_url, REDIRECT_FIELD_NAME, path
        return HttpResponseRedirect('%s?%s=%s' % tup)
    return wrap
