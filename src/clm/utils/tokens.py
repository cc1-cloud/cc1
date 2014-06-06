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

"""@package src.clm.utils.tokens

@author Piotr Wójcik
@date 21.09.2010
"""

from django.utils.http import int_to_base36, base36_to_int


class PasswordResetTokenGenerator(object):
    """
    Class for generating tokens during password reset.
    """
    def make_token(self, user):
        """
        @parameter{user,User} instance of the User whom Token should be
        generated for

        @returns{string} Token with timestamp generated for specified User
        """
        import hashlib
        h = hashlib.sha1(user.password +
                         unicode(user.last_login_date) +
                         unicode(user.id)).hexdigest()[::2]
        return "%s-%s" % (int_to_base36(user.id), h)

    def check_token(self, user, token):
        """
        @parameter{user,User} instance of the User whose Token should be
        checked.
        @parameter{token,string} Token to check

        @returns{bool} @val{true} for right Token, @val{false} for wrong Token
        """
        try:
            ts_b36 = token.split("-")[0]
        except ValueError:
            return False

        try:
            uid = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the uid has not been tampered with
        if uid != user.id:
            return False

        if self.make_token(user) != token:
            return False

        return True

default_token_generator = PasswordResetTokenGenerator()
