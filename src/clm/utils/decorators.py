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

"""@package src.clm.utils.decorators
Here are placed decorators for CLM views functions targeted to specific CLM
role actors (and src.clm.utils.decorators.genericlog() called by all those).

@par Actor decorators
- src.clm.utils.decorators.guest_log
- src.clm.utils.decorators.user_log
- src.clm.utils.decorators.admin_clm_log

All those decorators call src.clm.utils.decorators.genericlog().
By default those decorators call src.clm.utils.decorators.genericlog
with logging disabled. You can enable it by giving kwarg \c log=True ,
when decorating, eg.:

@code
@admin_clm_log(log=True)
def get_by_id(cm_id, caller_id, id):
    pass
@endcode

@author Tomasz Sośnicki <tom.sosnicki@gmail.com>
"""

from clm.utils.cm import CM
from clm.utils import log
from clm.utils.exception import CLMException
from clm.models.user import User
from common.signature import Signature
from common import response
from common.states import user_active_states

from functools import wraps
import json
from django.http import HttpResponse
from django.db import transaction


# Set of functions decorated by actor decorators
#  (clm.utils.decorators.guest_log(), src.clm.utils.decorators.user_log(),
#  src.clm.utils.decorators.admin_clm_log())
from common.utils import json_convert

global decorated_functions
decorated_functions = set([])


def guest_log(*arg, **kw):
    """
    Decorator for functions requiring only \b guest's privilidges.

    src.clm.utils.decorators.genericlog() is called with parameters:
    - \c is_user=False
    - \c is_clm_superuser=False
    - \c is_cm_superuser=False

    @par Decorated function's declaration
    @code
    @guest_log[(log=<False|True>)]
    function (**kw)
    @endcode

    @par Decorated function's call
    @code
    function (**kw)
    @endcode
    """
    def logwrapper(fun):

        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(kw.get('log', False), kw.get('pack', True), False, False, False, fun, args, kwargs)

        decorated_functions.add(wrapper)

        return wrapper
    return logwrapper


def user_log(*arg, **kw):
    """
    Decorator for functions requiring logged in \b user's privilidges.

    src.clm.utils.decorators.genericlog() is called with parameters:
    - \c is_user=True
    - \c is_clm_superuser=False
    - \c is_cm_superuser=False

    @par Decorated function's declaration
    @code
    @user_log[(log=<False|True>)]
    function (cm_id, caller_id, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (cm_id=<cm_id>, login=<login>, password=<password>, **kw)
    @endcode
    """
    def logwrapper(fun):

        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(kw.get('log', False), kw.get('pack', True), True, False, False, fun, args, kwargs)

        decorated_functions.add(wrapper)

        return wrapper

    return logwrapper


def admin_cm_log(*arg, **kw):
    """
    Decorator for functions requiring \b admin_cm's privilidges.

    src.clm.utils.decorators.genericlog is called with parameters:
    - \c is_user=True
    - \c is_clm_superuser=False
    - \c is_cm_superuser=True

    @par Decorated function's declaration
    @code
    @admin_clm_log[(log=<False|True>)]
    function (cm_id, caller_id, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (cm_id=<cm_id>, login=<login>, password=<password>, **kw)
    @endcode

    \c password argument is removed by \c src.cm.utils.decorators.genericlog(),
    so it doesn't appear in formal parameters of the function.
    """
    def logwrapper(fun):

        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(kw.get('log', False), kw.get('pack', True), True, False, True, fun, args, kwargs)

        decorated_functions.add(wrapper)

        return wrapper

    return logwrapper


def admin_clm_log(*arg, **kw):
    """
    Decorator for functions requiring \b admin_clm's privilidges.

    src.clm.utils.decorators.genericlog is called with parameters:
    - \c is_user=True
    - \c is_clm_superuser=True
    - \c is_cm_superuser=False

    @par Decorated function's declaration
    @code
    @admin_clm_log[(log=<False|True>)]
    function (cm_id, caller_id, *args, **kw)
    @endcode

    @par Decorated function's call
    @code
    function (cm_id, login, password, *arg, **kw)
    @endcode

    \c password argument is removed by \c src.cm.utils.decorators.genericlog(),
    so it doesn't appear in formal parameters of the function.
    """
    def logwrapper(fun):

        @wraps(fun)
        def wrapper(*args, **kwargs):
            return genericlog(kw.get('log', False), kw.get('pack', True), True, True, False, fun, args, kwargs)

        decorated_functions.add(wrapper)

        return wrapper

    return logwrapper


def auth(is_user, is_clm_superuser, data):
    if is_user:
        login = data.pop('login')
        password = data.get('password')

        if password:
            del data['password']
        try:
            user = User.objects.get(login=login)
        except User.DoesNotExist:
            raise CLMException('user_get')

        if 'Signature' in data.keys():
            if not Signature.checkSignature(user.password, data.pop('Signature'), data['parameters']):
                raise CLMException('user_get')
            del data['parameters']
        elif user.password != password:
            raise CLMException('user_get')

        data['caller_id'] = user.id
        if user.is_active != user_active_states['ok']:
            raise CLMException('user_inactive')
        if is_clm_superuser and not user.is_superuser:
            raise CLMException('user_permission')

        data['cm_id'] = data.pop('cm_id', None)
        if not data['cm_id']:
            if user.default_cluster_id is not None:
                data['cm_id'] = user.default_cluster_id

        return user.id
    else:
        return 0


def genericlog(log_enabled, pack_resp, is_user, is_clm_superuser, is_cm_superuser, fun, args, kwargs):
    """
    Generic log is called by actor decorators defined in src.clm.utils.decorators :
    - src.clm.utils.decorators.guest_log
    - src.clm.utils.decorators.user_log
    - src.clm.utils.decorators.admin_cm_log
    - src.clm.utils.decorators.admin_clm_log

    It calls decorated functions, additionally performing several tasks.

    Genericlog performes:

    -# <i>if decorated function requires user or admin privilidges</i>: <b>authorization</b>;
    -# <b>execution</b> of the decorated function;
    -# <b>debug log</b> of the arguments <i>depending on \c log_enabled and function's success</i>;
    -# <i>if exception is thrown</i>: <b>general exception log</b>.

    @returns{dict} response; fields:
    @dictkey{status,string} 'ok', if succeeded
    @dictkey{data,dict} response data
    """
    #===========================================================================
    # AUTORIZATION
    #===========================================================================
    name = '%s.%s' % (fun.__module__.replace('clm.views.', ''), fun.__name__)

    request = args[0]

    data = json.loads(request.body)
    #===========================================================================
    # LOG AGRUMENTS
    #===========================================================================
    gen_exception = False

    with transaction.commit_manually():
        try:
            # Execute function
            user_id = auth(is_user, is_clm_superuser, data)
            resp = fun(**data)
            if pack_resp and not hasattr(fun, 'packed'):  # if function is decorated by cm_request, 'packed' atribbute will be set - response is already packed by cm
                resp = response('ok', resp)
            transaction.commit()
        except CLMException, e:
            transaction.rollback()
            user_id = 0
            resp = e.response
        except Exception, e:
            transaction.rollback()
            gen_exception = True
            user_id = 0
            resp = response('clm_error', str(e))

    if log_enabled or resp['status'] != 'ok':
        log.debug(user_id, '=' * 100)
        log.debug(user_id, 'Function: %s' % name)
        log.debug(user_id, 'ARGS:\n%s' % json.dumps(data, indent=4))
        if gen_exception:
            log.exception(user_id, 'General exception')
        log.debug(user_id, 'Response: %s' % resp or 'None')

    return HttpResponse(json.dumps(resp, default=json_convert))


def cm_request(fun):
    """
    Decorator for CM views functions that:
    - either are fully transparent and just return CM response,
    - or propagate request to CM and further postprocess its response.

    Decorated function ought to be defined like:

    @par Decorated function's declaration
    @code
    @cm_request
    def function (cm_response, <kwargs>):
        # postprocess cm_response
        return cm_response
    @endcode

    @par Decorated function's call
    @code
    function (cm_id, <kwargs>) # `cm_id` is keyword arg as well, but it's required
    @endcode
    """
    url = r"%s/%s/" % (fun.__module__.replace("clm.views.", "").replace(".", "/"), fun.__name__)

    @wraps(fun)
    def wrapper(**data):
        log.debug(0, "Forward request to CM: %s" % url)
        cm_response = CM(data.pop('cm_id')).send_request(url, **data)
        fun.packed = True  # mark function response to not be packed by genericlog
        return fun(cm_response, **data)
    return wrapper

