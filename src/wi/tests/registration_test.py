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
"""@package src.wi.tests.registration_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 11.10.2012
"""

from wi.tests import WiTestCase
import unittest
import random


class RegistrationTests(WiTestCase, unittest.TestCase):

    def _fill_common_data(self, field_key=None, field_value=None):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        driver.get(self.base_url + "/registration/register/")

        self.change_language()

        self.wait_for_text("//div[@id='content']/div[2]/div/div[5]/h2", ["Registration"])

        driver.find_element_by_id("id_login").clear()
        driver.find_element_by_id("id_login").send_keys("witest" + str(random.randint(1, 100000)))
        driver.find_element_by_id("id_first").clear()
        driver.find_element_by_id("id_first").send_keys("test")
        driver.find_element_by_id("id_last").clear()
        driver.find_element_by_id("id_last").send_keys("test")
        driver.find_element_by_id("id_organization").clear()
        driver.find_element_by_id("id_organization").send_keys("test")
        driver.find_element_by_id("id_email").clear()
        driver.find_element_by_id("id_email").send_keys("witest" + str(random.randint(1, 100000)) + "@witest.pl")
        driver.find_element_by_id("id_new_password").clear()
        driver.find_element_by_id("id_new_password").send_keys("test1")
        driver.find_element_by_id("id_password2").clear()
        driver.find_element_by_id("id_password2").send_keys("test1")

        if field_key is not None:
            driver.find_element_by_id(field_key).clear()
            driver.find_element_by_id(field_key).send_keys(field_value)

        driver.find_element_by_css_selector("input.big_button").click()

    @unittest.skip('a')
    def test_1_registration_success(self):
        driver = self.driver
        self._fill_common_data()
        self.assertEqual("Registration success - Registration - CC1", driver.title)

    def test_2_registration_login_duplicate(self):
        self._fill_common_data("id_login", self.TEST_USER['login'])
        self.wait_for_text("//form[@id='registration-form']/fieldset/div/ul/li", ["A user with that login already exists."])

    def test_3_registration_wrong_email(self):
        self._fill_common_data("id_email", "witest" + str(random.randint(1, 100000)) + "@witestpl")
        self.wait_for_text("//form[@id='registration-form']/fieldset/div/ul/li", ["Enter a valid email address."])
