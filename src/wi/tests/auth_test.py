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

# -*- coding: utf-8 -*-
"""@package src.wi.tests.auth_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 11.10.2012
"""

from wi.tests import WiTestCase
import unittest


class Login(WiTestCase, unittest.TestCase):
    def test_login(self):
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)
        self.wait_for_text("//div[@id='header']/ul/li", ["Logged as test_user |"])
