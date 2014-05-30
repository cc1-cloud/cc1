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

"""@package src.cm.utils.decorators
Here are placed decorators for:
- \b actor functions
(and the src.cm.utils.decorators.genericlog() function called by all those),
- \b ctx functions,
- \b rm functions.


@par Actor decorators
- src.cm.utils.decorators.guest_log
- src.cm.utils.decorators.user_log
- src.cm.utils.decorators.admin_cm_log

Those actor decorators call src.cm.utils.decorators.genericlog().
By default those decorators call src.cm.utils.decorators.genericlog
with logging disabled. You can enable it by giving kwarg \c log=True ,
when decorating, eg.:


@code
@admin_clm_log(log=False)
def get_by_id(cm_id, caller_id, id):
    pass
@endcode
@author Tomasz Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <mn@mnabozny.pl>
"""
from cm.utils import log
from cm.utils.exception import CMException
from common import response  # HandleQuerySets
from cm.models.admin import Admin
from functools import wraps
import json
from django.http import HttpResponse
from django.db import transaction
from threading import Lock

# # Set of functions decorated by actor decorators
#  (cm.utils.decorators.guest_log(), src.cm.utils.decorators.user_log(),
#  src.cm.utils.decorators.admin_cm_log())
from common.utils import json_convert

global decorated_functions
global ci_decorated_functions
global ctx_decorated_functions

decorated_functions = set([])
ci_decorated_functions = set([])
ctx_decorated_functions = set([])


locks = {
    'vmcreate': Lock()
}

# Every actor decorators add the decorated function to global decorated_functions and send it
# to genericlog but with different arguments


def guest_log(*arg, **kw):
    """
    Decorator for functions requiring only \b guest's privilidges.

    src.cm.utils.decorators.genericlog() is called with parameters:
    - \c is_user=False
    - \c is_superuser=False

    @par Decorated function's declaration
    @code
    @guest_log[(log=<False|True>)]
    function (*arg, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (*arg, **kw)
    @endcode
    """
    def logwrapper(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(log_enabled=kw.get('log', False), is_user=False, is_admin_cm=False, need_ip=False, fun=fun, args=args)

        decorated_functions.add(wrapper)

        return wrapper
    return logwrapper


def user_log(*arg, **kw):
    """
    Decorator for functions requiring logged in \b user's privilidges.

    src.cm.utils.decorators.genericlog() is called with parameters:
    - \c is_user=True
    - \c is_superuser=False

    @par Decorated function's declaration
    @code
    @user_log[(log=<False|True>)]
    function (cm_id, caller_id, *args, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (caller_id, *arg, **kw)
    @endcode
    """
    def logwrapper(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(log_enabled=kw.get('log', False), is_user=True, is_admin_cm=False, need_ip=False, fun=fun, args=args)

        decorated_functions.add(wrapper)

        return wrapper
    return logwrapper


def admin_cm_log(*arg, **kw):
    """
    Decorator for functions requiring \b admin_cm's privilidges.

    src.cm.utils.decorators.genericlog is called with parameters:
    - \c is_user=True
    - \c is_superuser=True

    @par Decorated function's declaration
    @code
    @admin_clm_log[(log=<False|True>)]
    function (cm_id, caller_id, *args, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (caller_id, admin_password, *arg, **kw)
    @endcode

    \c admin_password argument is removed by
    \c src.cm.utils.decorators.genericlog(), so it doesn't appear in formal
    parameters of the function.
    """
    def logwrapper(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(log_enabled=kw.get('log', False), is_user=True, is_admin_cm=True, need_ip=False, fun=fun, args=args)

        decorated_functions.add(wrapper)

        return wrapper
    return logwrapper


def ci_log(*arg, **kw):
    """
    Decorator for functions requiring only \b guest's privilidges.

    src.cm.utils.decorators.genericlog() is called with parameters:
    - \c is_user=False
    - \c is_superuser=False

    @par Decorated function's declaration
    @code
    @guest_log[(log=<False|True>)]
    function (*arg, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (*arg, **kw)
    @endcode
    """
    def logwrapper(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(log_enabled=kw.get('log', False), is_user=False, is_admin_cm=False, need_ip=True, fun=fun, args=args)

        ci_decorated_functions.add(wrapper)

        return wrapper
    return logwrapper


def ctx_log(*arg, **kw):
    """
    Decorator for functions requiring only \b guest's privilidges.

    src.cm.utils.decorators.genericlog() is called with parameters:
    - \c is_user=False
    - \c is_superuser=False

    @par Decorated function's declaration
    @code
    @guest_log[(log=<False|True>)]
    function (*arg, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (*arg, **kw)
    @endcode
    """
    def logwrapper(fun):
        @wraps(fun)
        def wrapper(request, *args, **kwargs):
            data = request.GET.dict()
            data['remote_ip'] = request.META.get('REMOTE_ADDR')
            #log.debug(0, 'RAW ARGS: %s' % str(data))

            gen_exception = False
            log_enabled = kw.get('log', False)
            name = '%s.%s' % (fun.__module__.replace('cm.views.', ''), fun.__name__)
            if log_enabled:
                log.debug(0, '=' * 100)
                log.debug(0, 'Function: %s' % name)
                log.debug(0, 'Args:\n%s' % json.dumps(data, indent=4))
            with transaction.commit_manually():
                try:
                    # Execute function
                    resp = fun(**data)
                    transaction.commit()
                except CMException, e:
                    transaction.rollback()
                    log.exception(0, 'CMException %s' % e)
                    resp = e.response
                except Exception, e:
                    transaction.rollback()
                    gen_exception = True
                    resp = response('cm_error', str(e))

            if resp['status'] != 'ok' and not log_enabled:
                log.debug(0, '=' * 100)
                log.debug(0, 'Function: %s' % name)
                log.debug(0, 'ARGS: %s' % str(data))
            if resp['status'] != 'ok' or log_enabled:
                if gen_exception:
                    log.exception(0, 'General exception')
                log.debug(0, 'Response: %s' % resp or 'None')

            return HttpResponse(json.dumps(resp, default=json_convert))

        ctx_decorated_functions.add(wrapper)

        return wrapper
    return logwrapper


def ec2ctx_log(*arg, **kw):
    """
    Decorator for functions requiring only \b guest's privilidges.

    src.cm.utils.decorators.genericlog() is called with parameters:
    - \c is_user=False
    - \c is_superuser=False

    @par Decorated function's declaration
    @code
    @guest_log[(log=<False|True>)]
    function (*arg, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (*arg, **kw)
    @endcode
    """
    def logwrapper(fun):
        @wraps(fun)
        def wrapper(request, *args, **kwargs):
            log.debug(0, "request\n%s: " % json.dumps(request.GET.dict(), indent=4))
            log_enabled = kw.get('log', False)
            name = '%s.%s' % (fun.__module__.replace('cm.views.', ''), fun.__name__)
            if log_enabled:
                log.debug(0, '=' * 100)
                log.debug(0, 'Function: %s' % name)

            resp = None
            try:
                resp = fun(request, *args, **kwargs)
            except CMException, e:
                log.exception(0, 'CMException %s' % e)
            except Exception, e:
                log.exception(0, 'Exception %s' % e)

            return HttpResponse(resp)
        return wrapper
    return logwrapper


def genericlog(log_enabled, is_user, is_admin_cm, need_ip, fun, args):
    """
    Generic log is called by actor decorators defined in src.clm.utils.decorators :
    - src.cm.utils.decorators.guest_log
    - src.cm.utils.decorators.user_log
    - src.cm.utils.decorators.admin_cm_log

    It calls decorated functions, additionally performing several tasks.

    Genericlog performes:

    -# <i>if decorated function requires user or admin privilidges</i>: <b>authorization</b>;
    -# <b>execution</b> of the decorated function;
    -# <i>if \c log_enabled=TRUE or if return status isn't 'ok'</i>: <b>debug log</b> of the \c user_id, function name and arguments;
    -# <i>if exception is thrown</i>: <b>general exception log</b>;
    -# <i>if return status isn't 'ok' or \c log_enabled:</i> <b>debug log</b> of the response.

    @returns{dict} HttpResponse response with content of JSON-ed tuple
    (status, data), where status should be "ok" if everything went fine.
    """
    #===========================================================================
    # AUTORIZATION
    #===========================================================================
    name = '%s.%s' % (fun.__module__.replace('cm.views.', ''), fun.__name__)

    request = args[0]
    #log.debug(0, 'BODY: %s' % request.body)
    data = json.loads(request.body)

    lock_name = None
    print data

    if is_user:
        if len(args) < 1:
            return response('cm_error', "missing arguments")

        caller_id = data['caller_id']

        if name in ('user.vm.create', 'user.farm.create', 'admin_cm.vm.create', 'admin_cm.farm.create'):
            lock_name = 'vmcreate'
            log.debug(caller_id, 'Try acquire lock vmcreate')
            locks[lock_name].acquire()
            log.debug(caller_id, 'Lock vmcreate acquired')

        if is_admin_cm:
            cm_password = data.pop('cm_password')
            try:
                Admin.check_password(caller_id, cm_password)
            except Exception:
                return HttpResponse(json.dumps(response('user_permission'), default=json_convert))
    else:
        caller_id = 0

    if need_ip:
        data['remote_ip'] = request.META.get('REMOTE_ADDR')

    #===========================================================================
    # LOG AGRUMENTS
    #===========================================================================
    gen_exception = False
    if log_enabled:
        log.debug(caller_id, '=' * 100)
        log.debug(caller_id, 'Function: %s' % name)
        log.debug(caller_id, 'Args:\n%s' % json.dumps(data, indent=4))

    with transaction.commit_manually():
        try:
            # Execute function
            resp = response('ok', fun(**data))
            transaction.commit()
        except CMException, e:
            transaction.rollback()
            log.exception(caller_id, 'CMException %s' % e)
            resp = e.response
        except Exception, e:
            transaction.rollback()
            gen_exception = True
            resp = response('cm_error', str(e))
        finally:
            if lock_name:
                log.debug(caller_id, 'Try release lock vmcreate')
                locks[lock_name].release()
                log.debug(caller_id, 'Lock vmcreate released')
    # adding messages to response
    global MESSAGES
    if MESSAGES:
        resp['messages'] = MESSAGES.copy()
        MESSAGES.clear()
    if resp['status'] != 'ok' and not log_enabled:
        log.debug(caller_id, '=' * 100)
        log.debug(caller_id, 'Function: %s' % name)
        log.debug(caller_id, 'ARGS: %s' % str(data))
    if resp['status'] != 'ok' or log_enabled:
        if gen_exception:
            log.exception(caller_id, 'General exception')
        log.debug(caller_id, 'Response: %s' % resp or 'None')
    return HttpResponse(json.dumps(resp, default=json_convert))
