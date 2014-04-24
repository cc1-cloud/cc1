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
"""@package src.wi.tests.help_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 10.12.2012
"""

from wi.tests import WiTestCase
import unittest


class Help(WiTestCase, unittest.TestCase):
    def test_1_help_guest(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        driver.get(self.base_url + "/auth/login/")
        self.change_language()

        driver.find_element_by_link_text("Help").click()
        self.wait_for_text("//div[@id='content']/div[3]/div/div[5]/h2", ["Help"])
        self.assertEqual("Help - CC1", driver.title)

    def test_2_help_user(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/help/form/")
        driver.find_element_by_link_text("Help").click()
        driver.find_element_by_link_text("Contact form").click()
        self.wait_for_text("//div[@id='content']/div[3]/div/div[5]/h2", ["Contact form"])
        self.assertEqual("Contact form - Help - CC1", driver.title)
