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
"""@package src.wi.tests.cm_templates_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 31.01.2013
"""

from wi.tests import WiTestCase
import random
import unittest


class CMTemplatesTests(WiTestCase, unittest.TestCase):
    def _test_add_template(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/templates/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Create a new template"])

        driver.find_element_by_link_text("Create a new template").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        name = "witest_template" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys("witest")
        driver.find_element_by_id("id_points").clear()
        driver.find_element_by_id("id_points").send_keys("1")
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully created a template."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_edit_template(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/templates/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit")

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        newname = "new_witest_template" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited selected template."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        return newname

    def _test_remove_template(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/templates/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Delete")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to delete template"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully deleted template"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_send_request(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/templates/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit")

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        newname = "new_witest_template" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited selected template."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        return newname

    def test_1_simple(self):
        name = self._test_add_template()
        newname = self._test_edit_template(name)
        self._test_remove_template(newname)
