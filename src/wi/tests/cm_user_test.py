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
"""@package src.wi.tests.cm_users

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 22.03.2013
"""

from wi.tests import WiTestCase
import unittest


class CMUsersTests(WiTestCase, unittest.TestCase):
    def _test_set_admin(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/users/")

        self.wait_for_text("//table[@id='item-list']/tbody", ["test_user"])

        self.menu_click("Username", "test_user", "Set admin")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to promote user"])

        driver.find_element_by_id("id_new_password").clear()
        driver.find_element_by_id("id_new_password").send_keys("cokolwiek")
        driver.find_element_by_id("id_password2").clear()
        driver.find_element_by_id("id_password2").send_keys("cokolwiek")

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully promoted user "])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_unset_admin(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/users/")

        self.wait_for_text("//table[@id='item-list']/tbody", ["test_user"])

        self.menu_click("Username", "test_user", "Unset admin")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to demote administrator"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully demoted administrator"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_change_quota(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/users/")
        self.wait_for_text("//table[@id='item-list']/tbody", ["test_user"])

        self.cell_click("Username", "test_user", action_name="", element="input")

        driver.find_element_by_xpath("//li[@id='group_action']/a").click()

        self.wait_for_text("//ul[@id='context-menu-list']/li", ["Change quota"])

        driver.find_element_by_xpath("//ul[@id='context-menu-list']/li").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Cpu Total"])

        driver.find_element_by_id("id_cpu").clear()
        driver.find_element_by_id("id_cpu").send_keys("12")

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully changed quota."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_change_quota_account(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/users/")

        self.wait_for_text("//table[@id='item-list']/tbody", ["test_user"])

        self.menu_click("Username", "test_user", "User account")

        self.wait_for_text("//div[@id='user-data']/fieldset/div/span[2]", ["test_user"])

        driver.find_element_by_link_text("Edit account quota").click()

        driver.find_element_by_id("id_cpu").clear()
        driver.find_element_by_id("id_cpu").send_keys("20")

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully changed the user's quota."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def test_1_simple(self):
        self._test_set_admin()
        self._test_unset_admin()
        self._test_change_quota()
        self._test_change_quota_account()
