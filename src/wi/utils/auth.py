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

"""@package src.wi.utils.auth

@author Piotr Wójcik
@date 21.09.2010
"""

from wi.models.user import parse_user
from wi.utils.views import make_request

session_key = '_auth_user_id'


def authenticate(username, password):
    """
    Method for authentication. When successful, it returns \c user object.
    """
    response = make_request('guest/user/check_password/', {'login': username, 'password': password})
    if response['status'] == 'ok' and response['data']:
        return parse_user(response['data'])
    return None


def login(request, user):
    """
    Saves \c user in session.
    """
    if session_key in request.session:
        if request.session[session_key] != user.user_id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    request.session[session_key] = user.user_id
    request.session['user'] = user


def logout(session):
    """
    Removes data connected with user from the session.
    """
    session.flush()


def cm_authenticate(user, password, cm_id):
    """
    CM admin authentication. Returns True if successful.

    @parameter{user}
    @parameter{password}
    @parameter{cm_id}
    """
    rest_data = make_request('user/admin/check_password/', {'cm_password': password}, user=user)
    return True if rest_data['status'] == 'ok' else False


def cm_login(session, cm_password, cm_id):
    """
    Stores CM admin specific data in session.
    """
    session['user'].cm_password = cm_password
    session['user'].cm_id = int(cm_id)
    session['user'].is_logged_admin_cm = True
    session.modified = True


def cm_logout(session):
    """
    Cleans CM admin specific data from session.
    """
    session['user'].is_logged_admin_cm = False
    session.modified = True
