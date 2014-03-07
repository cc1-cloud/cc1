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
"""@package src.wi.tests.cm_networks_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 09.01.2013
"""

from wi.tests import WiTestCase
import unittest


class CMNetworksTests(WiTestCase, unittest.TestCase):

    @staticmethod
    def _test_add_pool(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/pools/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Add pool"])

        driver.find_element_by_link_text("Add pool").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Pool address"])

        driver.find_element_by_id("id_address").clear()
        driver.find_element_by_id("id_address").send_keys("10.10.127.0")
        driver.find_element_by_id("id_mask").clear()
        driver.find_element_by_id("id_mask").send_keys("24")
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully added a pool."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_unlock_pool(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/pools/")

        self.wait_for_text("//table[@id='item-list']/tbody", ["10.10.127.0"])

        self.menu_click("Address", "10.10.127.0", "Unlock")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to unlock pool"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully unlocked pool"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_lock_pool(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/pools/")

        self.wait_for_text("//table[@id='item-list']/tbody", ["10.10.127.0"])

        self.menu_click("Address", "10.10.127.0", "Lock")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to lock pool"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully locked pool"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_delete_pool(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/pools/")

        self.wait_for_text("//table[@id='item-list']/tbody", ["10.10.127.0"])

        self.menu_click("Address", "10.10.127.0", "Delete")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to delete pool"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully deleted pool"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def test_1_simple(self):
        self._test_add_pool(self)
        self._test_lock_pool()
        self._test_unlock_pool(self)
        self._test_delete_pool(self)
