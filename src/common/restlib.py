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

"""@package src.common.restlib
"""

from argparse import ArgumentError, ArgumentTypeError
import json
import logging
import re
import requests
from django.conf.urls import url, patterns
from django.http import HttpResponse
import inspect


class ServerProxy(object):
    """
    Wrapper class around REST like calls to cc1 functions.

    usage:

    :::python
    #s = ServerProxy("http://samplehost:port")
    ## maps to http://samplehost:port/module1/f1
    #r = s.module1.f1(arg1, arg2, kwarg1=val, ...)
    ## maps to http://samplehost:port/f1
    #r = s.f1(arg1)
    ## maps to http://samplehost:port/module1/submodule2/f1
    #r = s.module1.submodule2.f1(arg1, arg2, kwarg1=val, kwarg2=val)


    returned value is unwrapped from json so it can be readily used.
    Depending on status codes approperiate Exceptions are raised

    """
    class RemoteCaller(object):
        """
        Hepler class used as a simple mapper of dot notation to URL notation, as well as encoding passed arguments to JSON
        and decoding response from JSON
        """

        def __init__(self, server_proxy, function_name, logger=None):
            self.server_proxy = server_proxy
            # :type: string
            self.function_name = function_name
            if logger:
                self.logger = logger
            else:
                logger = logging.getLogger()
                # effectivly disable logging
                logger.setLevel(100)

        def __call__(self, *args, **kwargs):
            self.logger.info("called %s/%s   body: %s" %
                              (self.server_proxy.server_address,
                               self.function_name,
                               json.dumps({"args": args, "kwargs": kwargs})))

            r = requests.get("%s/%s" % (self.server_proxy.server_address, self.function_name),
                             data=json.dumps({"args": args, "kwargs": kwargs}))

            self.logger.info("response from %s/%s    is:%s" % (self.server_proxy.server_address,
                                                                self.function_name, r))

            if not r.ok:
                self.logger.error("HTTP response is not 200, error occured: %s with data: %s" % (r.status_code,
                                                                                                 r.text))
                raise Exception("Status %s failed to call function" % r.status_code)
            r = json.loads(r.text)
            if not isinstance(r, dict):
                self.logger.error("Returned object is %s expected dict. Data: %s" % (type(r), r))
                raise Exception("Returned object is %s expected dict" % type(r))
            if 'status' not in r or 'data' not in r:
                self.logger.error("Returned object is malformatted: %s" % r)
                raise Exception("Returned object is malformatted: %s" % r)
            return r

        def __getattr__(self, item):
            self.function_name = "%s/%s" % (self.function_name, item)
            self.logger.debug("called . on RemoteCaller. Current address string is: %s/%s" %
                              (self.server_proxy.server_address, self.function_name))
            return self

    def __init__(self, server_address, log_level=100, logger=None):
        """
        :param log_level: this argument is used only if no external logger is supplied. It sets reporting level for an
                          on screen logging Handler. if logger is supplied this argument has no effect. (logging level
                          is defined in handlers connected to that logger)
                          level should be specified as one of the constants defined in logging module:
                          - 100 (effectively disables logging) //default
                          - logging.CRITICAL
                          - logging.ERROR
                          - logging.WARNING / logging.WARN
                          - logging.INFO
                          - logging.DEBUG


        :type log_level: int
        :param logger: Logger object to which logging will be performed, defaults to None (in this case all logging is
                       send to screen
        :type logger: logging.Logger
        :param server_address: server address in format protocol://host:port
                               protocol must be http or https (without certificate checking)
                               server_address can not end with slash '/'
        :type server_address: str
        """

        if logger:
            self.logger = logger
        else:
            h = logging.StreamHandler()
            h.setLevel(log_level)
            self.logger = logging.getLogger()
            self.logger.setLevel(log_level)
            self.logger.addHandler(h)

        self.server_address = server_address
        if not re.match(r'^(http)s?://[a-zA-Z0-9\.]+(:\d+)?/([a-zA-Z0-9]+/)*$', self.server_address):
            self.logger.error("%s is not well formatted address" % self.server_address)
            raise ValueError("%s is not well formatted address" % self.server_address)

    def __getattr__(self, item):
        return ServerProxy.RemoteCaller(self, item, logger=self.logger)


def register_object(object_to_register, prefix='', decorator=None):
    """
    Generates list of django urls pointing to all public (not starting with '_') methods of the supplied object

    generated urls is in form:

    #prefix/name_of_first_public_method
    #prefix/name_of_second_public_method
    #prefix/name_of_third_public_method
    #...

    :param object_to_register:
    :type object_to_register: object
    :param prefix: prefix can not start with the '/' character (same as django urls)
    :type prefix: str
    :param decorator: decorator applied to function before calling it by JSONWrapper (default=None)
    :type decorator: function
    :return: :raise ArgumentError: returns list of django urls
    :rtype: list
    """
    if len(prefix) > 0 and prefix[0] == '/':
        raise ArgumentError("prefix can not start with '/'")
    members = inspect.getmembers(object_to_register, predicate=inspect.ismethod)
    urls = []
    for method_name, function in members:
        if not method_name[0] == "_":
            urls += register_function(function, prefix, decorator)
    return urls


def register_function(function_to_register, prefix='', decorator=None, log_name=None, logger=None):
    """
    Generates list containing single django url pointing to suppled function

    generated url is in form:

    #prefix/name_of_registered_function

    :param function_to_register: function to which sensible django url should be generated. This argument can be either
                                 callable object, or tuple having form (callable, "rest_call_name") where second element
                                 of tuple will be name under which function will be registered. Else defaults to
                                 function_to_register.__name__, this functionality should not be used, except for
                                 situations when decorators apart from the one supplied as argument of this function
                                 are present
    :type function_to_register: __builtin__.callable or tuple
    :param prefix: prefix can not start with the '/' character (same as django urls)
    :type prefix:
    :param decorator: decorator applied to function before calling it by JSONWrapper (default=None)
    :type decorator: function
    :param log_name: this name will be used with logging and error functions, defaults to function_to_register.__name__
                     or if decorator parameter is supplied to "@decorator.__name__(function_to_register.__name__)"
    :type log_name: str
    :return: :raise ArgumentError: returns list of django urls
    :rtype: list
    """

    if len(prefix) > 0 and prefix[0] == '/':
        raise ArgumentError("prefix can not start with '/'")

    if isinstance(function_to_register, tuple):
        rest_call_name = function_to_register[1]
        function_to_register = function_to_register[0]
    else:
        rest_call_name = function_to_register.__name__

    function_to_call = JsonWrapper(function_to_register, function_to_call_name=log_name or function_to_register.__name__, logger=logger)
    if decorator is not None:
        function_to_call = JsonWrapper(decorator(function_to_register),
                                       function_to_call_name=log_name or "@%s(%s)" % (decorator.__name__,
                                                                                      function_to_register.__name__), logger=logger)

    urls = patterns('', url("^%s%s" % (prefix, rest_call_name), function_to_call))
    return urls


def register_functions(*args, **kwargs):
    """
    called in form:
    :::python
    #with default prefix '/'
    urls = register_functions(funct1, funct2, funct3, ...)
    #or with prefix
    urls = register_functions(funct1, funct2, funct3, ..., prefix="some/path/")
    #or with decorator
    urls = register_functions(funct1, funct2, funct3, ..., prefix="some/path/", decorator=my_decorator)


    Generates list of django urls pointing to all callables supplied as arguments

    generated url is in form:

    #prefix/name_of_first_registered_function
    #prefix/name_of_second_registered_function
    #prefix/name_of_third_registered_function
    #...


    :param functions_to_register:
    :type functions_to_register: __builtin__.callable
    :param prefix: prefix can not start with the '/' character (same as django urls)
    :type prefix: str
    :param decorator: decorator applied to function before calling it by JSONWrapper (default=None)
    :type decorator: function
    :return: :raise ArgumentError: returns list of django urls
    :rtype: list
    """
    prefix = kwargs.get('prefix', '')
    decorator = kwargs.get('decorator', None)
    urls = []
    for function in args:
        # check if argument is an function
        if not hasattr(function, '__call__'):
            raise ArgumentTypeError("supplied object is not callable")
        urls += register_function(function, prefix=prefix, decorator=decorator, logger=kwargs.get('logger'))
    return urls


class JsonWrapper(object):
    """
    wrapper object for callable object which provides abstraction layer for packing and unpacking json
    (to function arguments) as well as wrapping function return object into http request, as well as encoding exceptions
    raised by function into approperiate http status_codes.
    """

    def __init__(self, function_to_call, function_to_call_name=None, logger=None):
        """
        :param function_to_call_name: this name will be used with any error handling, defaults to function_to_call.__name__
                                      should be used in case of using decorators on base function
        :type function_to_call_name: str
        :param function_to_call: callable object which will be wrapped by JsonWrapper
        :type function_to_call: __builtin__.callable
        """
        self.function_to_call = function_to_call
        self.function_to_call_name = function_to_call_name or function_to_call.__name__
        self.logger = logger

    def __call__(self, request):
        """
        Wrapper around function call, it converts data passed in HTTPRequest into arguments for the wrapped callable

        :param request:
        :type request: django.http.HttpRequest
        :return: returns data returned by wrapped callable, encoded as JSON in body of the HTTPResonse object
                 (status_code depends on the success of call)
        :rtype: HttpResponse
        """

        fulljson = json.loads(request.body)
        args = fulljson.get('args')
        kwargs = fulljson.get('kwargs')
        kwargs['request'] = request
        try:
            r = self.function_to_call(*args, **kwargs)
            if not isinstance(r, dict):
                raise TypeError("object returned by %s is not dict" % self.function_to_call_name)
            if 'status' not in r:
                raise KeyError("object returned by %s does not contain key 'status'" % self.function_to_call_name)
            if 'data' not in r:
                raise KeyError("object returned by %s does not contain key 'data'" % self.function_to_call_name)
            return HttpResponse(json.dumps({"status": r['status'], "data": r['data']}))
        except KeyError as e:
            response = {"status": "KeyError", "data": e.message}
            return HttpResponse(json.dumps(response))
        except TypeError as e:
            response = {"status": "TypeError", "data": e.message}
        except BaseException as e:
            response = {"status": "call", "data": e.message}
        return HttpResponse(json.dumps(response))
