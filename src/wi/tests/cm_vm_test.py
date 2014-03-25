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
"""@package src.wi.tests.cm_vm_test
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 13.02.2013
"""

from wi.tests import WiTestCase
import unittest
import vm_test


class CMVMTests(WiTestCase, unittest.TestCase):
    def _test_destroy_vm(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/vms/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        driver.find_element_by_id("auto-refresh").click()
        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li[2]/a", ["Destroy"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li[2]/a").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to destroy virtual machine"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["successfully destroyed"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_erase_vm(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/vms/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        driver.find_element_by_id("auto-refresh").click()
        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li[3]/a", ["Erase"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li[3]/a").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to erase virtual machine"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["successfully erased"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_erase_multiple_vm(self, list):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/vms/")

        driver.find_element_by_id("auto-refresh").click()

        for name in list:
            self.wait_for_text("//table[@id='item-list']/tbody", [name])

            self.cell_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"}, "", "input")

        driver.find_element_by_xpath("//li[@id='group_action']/a").click()

        self.wait_for_text("//ul[@id='context-menu-list']/li", ["Erase"])

        driver.find_element_by_xpath("//ul[@id='context-menu-list']/li[2]").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to erase"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["successfully erased"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def test_1_destroy(self):
        name = vm_test.VMTests._test_create_vm(self)
        self._test_destroy_vm(name)

    def test_2_erase(self):
        name = vm_test.VMTests._test_create_vm(self)
        self._test_erase_vm(name)

    def test_3_multiple_erase(self):
        name = vm_test.VMTests._test_create_vm(self)
        name2 = vm_test.VMTests._test_create_vm(self)
        self._test_erase_multiple_vm([name2, name])
