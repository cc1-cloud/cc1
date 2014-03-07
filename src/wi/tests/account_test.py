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
"""@package src.wi.tests.account_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 12.10.2012
"""

from wi.tests import WiTestCase
import random
import unittest


class AccountTests(WiTestCase, unittest.TestCase):

    def _email_change(self, email):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)
        driver.get(self.base_url + "/account/account_data/")

        self.wait_for_text("//div[@id='user-data']/fieldset[2]/a", ["Edit account data"])

        driver.find_element_by_link_text("Edit account data").click()
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Email address"])

        driver.find_element_by_id("id_email").clear()
        driver.find_element_by_id("id_email").send_keys(email)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

    def test_account_change_email_ok(self):
        email = str(random.randint(1, 100000)) + '@witest.pl'
        self._email_change(email)
        self.wait_for_text("//div[@id='user-data']/fieldset/div[3]/span[2]", [email])

    def test_account_change_email_empty(self):
        self._email_change('')
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div[1]/ul/li", ["This field is required."])

    def test_account_change_email_error(self):
        self._email_change('aaaaaaaaa.de')
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div[1]/ul/li", ["Enter a valid email address."])

    def test_password_change(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)
        driver.get(self.base_url + "/account/password_change/")
        self.wait_for_text("//div[@id='content']/div[3]/div/div[5]/div[2]/p", ["Please enter your old password"])

        driver.find_element_by_id("id_old_password").clear()
        driver.find_element_by_id("id_old_password").send_keys(self.TEST_USER['password'])
        driver.find_element_by_id("id_new_password1").clear()
        driver.find_element_by_id("id_new_password1").send_keys(self.TEST_USER['password'])
        driver.find_element_by_id("id_new_password2").clear()
        driver.find_element_by_id("id_new_password2").send_keys(self.TEST_USER['password'])

        driver.find_element_by_css_selector("input.big_button").click()
        self.wait_for_text("//div[@id='content']/div[3]/div/div[5]/div[2]/p", ["Your password has been changed."])

    def test_account_chart(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)
        driver.get(self.base_url + "/account/account_quotas/")
        self.wait_for_text("//div[@id='user-data']/fieldset[2]/a", ["Point usage chart"])

        driver.find_element_by_link_text("Point usage chart").click()
        self.wait_for_text("//div[@id='flotChart']", ["monthly point limit"])

    def test_show_ec2_key(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)
        driver.get(self.base_url + "/account/account_data/")
        driver.find_element_by_link_text("Show").click()

        self.wait_for_text("//span[@id='ui-dialog-title-dialog-div']", ["Copy to clipboard:"])
        self.assertEqual("b444ac06613fc8d63795be9ad0beaf55011936ac", driver.find_element_by_css_selector("textarea").get_attribute("value"))
