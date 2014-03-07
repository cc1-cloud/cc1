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
"""@package src.wi.tests.groups_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 05.03.2013
"""

from wi.tests import WiTestCase
import unittest
import random


class GroupsTests(WiTestCase, unittest.TestCase):
    @staticmethod
    def _test_create_group(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/groups/my_groups/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Create a new group"])

        driver.find_element_by_link_text("Create a new group").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        name = "witest_group" + str(random.randint(1, 100000))

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys(name)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully created a group."])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_edit_group(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/groups/my_groups/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit")

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        newname = "new_witest_group" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited selected group."])

        driver.find_element_by_link_text("Logout").click()

        return newname

    @staticmethod
    def _test_remove_group(self, name, who=None):
        driver = self.driver
        self.base_url = self.TEST_SERVER
        if who != None:
            self.login_testuser(who)
        else:
            self.login_testuser(self.TEST_admin_cm)

        driver.get(self.base_url + "/groups/my_groups/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Remove")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to delete this group?"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully deleted this group."])

        driver.find_element_by_link_text("Logout").click()

    def _test_send_request(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)

        driver.get(self.base_url + "/groups/list_groups/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Send request")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to send a request?"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully sent a request"])

        driver.find_element_by_link_text("Logout").click()

    def _test_cancel_request(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/groups/my_groups/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Show details")

        self.wait_for_text("//table[@id='item-list']/tbody", ['TestCMAdmin'])

        self.menu_click("Name", 'TestCMAdmin', "Cancel")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to cancel request from user"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully canceled request from user "])

        driver.find_element_by_link_text("Logout").click()

    def _test_accept_request(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/groups/my_groups/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Show details")

        self.wait_for_text("//table[@id='item-list']/tbody", ['TestCMAdmin'])

        self.menu_click("Name", 'TestCMAdmin', "Accept")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to add user"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully added user "])

        driver.find_element_by_link_text("Logout").click()

    def _test_make_leader(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/groups/my_groups/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Show details")

        self.wait_for_text("//table[@id='item-list']/tbody", ['TestCMAdmin'])

        self.menu_click("Name", 'TestCMAdmin', "Make leader")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to change group leader to user "])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_text("//div[@class='b_innerContainer']/div[2]/div/p", ["TestCMAdmin"])

        driver.find_element_by_link_text("Logout").click()

    def _test_remove_user(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)

        driver.get(self.base_url + "/groups/my_groups/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Show details")

        self.wait_for_text("//table[@id='item-list']/tbody", ['Test'])

        self.menu_click("Name", 'TestUser', "Remove")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to remove user"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully removed user"])

        driver.find_element_by_link_text("Logout").click()

    def test_1_all(self):
        name = self._test_create_group(self)
        newname = self._test_edit_group(name)
        self._test_send_request(newname)
        self._test_cancel_request(newname)
        self._test_send_request(newname)
        self._test_accept_request(newname)
        self._test_make_leader(newname)
        self._test_remove_user(newname)
        self._test_remove_group(self, newname)
