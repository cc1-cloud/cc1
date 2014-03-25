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
"""@package src.wi.tests.vm_test
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 25.01.2013
"""

from wi.tests import WiTestCase
import random
import resources_test
import unittest


class VMTests(WiTestCase, unittest.TestCase):
    @staticmethod
    def _test_create_vm(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/create_vm/")

        self.wait_for_text("//div[@id='item-list']/div[2]/table/tbody", ["witest_complete"])

        self.cell_click("Name", "witest_complete", None, element="a",
                         path_head_tds="//div[@id='item-list']/div[1]/table/tbody/tr/td",
                         path_body_trs="//div[@id='item-list']/div[2]/table/tbody/tr")

        self.wait_for_text("//div[@id='item-list']/div[2]/table/tbody", ["small"])

        self.cell_click("Name", "small", None, element="a",
                         path_head_tds="//div[@id='item-list']/div[1]/table/tbody/tr/td",
                         path_body_trs="//div[@id='item-list']/div[2]/table/tbody/tr")

        self.wait_for_text("//form[@id='wizard-form']/div[2]/fieldset/div/span/label", ["Assign IP address"])

        driver.find_element_by_xpath("//div[@id='submit-div']/input").click()

        self.wait_for_text("//form[@id='wizard-form']/div[2]/fieldset/div/span/label", ["Name"])

        name = "witest_vm" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_3-name").clear()
        driver.find_element_by_id("id_3-name").send_keys(name)

        driver.find_element_by_css_selector("input.big_button").click()

        self.wait_for_message(["Virtual machine is being created."])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_edit_vm(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[4]/a", ["Edit"])

        driver.find_element_by_link_text("Edit").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Name"])

        newname = "new_witest_vm" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited virtual machine data."])

        driver.find_element_by_link_text("Logout").click()

        return newname

    @staticmethod
    def _test_destroy_vm(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[1]/a", ["Destroy"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[1]/a").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to destroy virtual machine"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["successfully destroyed"])

        driver.find_element_by_link_text("Logout").click()

    def _test_enable_vnc(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[12]/td/div/ul/li/a", ["Enable VNC"])

        driver.find_element_by_link_text("Enable VNC").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to enable VNC?"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully enabled VNC."])

        driver.find_element_by_link_text("Logout").click()

    def _test_disable_vnc(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[12]/td/div/ul/li/a", ["Disable VNC"])

        driver.find_element_by_link_text("Disable VNC").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to disable VNC?"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully disabled VNC."])

        driver.find_element_by_link_text("Logout").click()

    def _test_reset_vm(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[3]/a", ["Reset"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[3]/a").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to reset virtual machine"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["successfully rebooted"])

        driver.find_element_by_link_text("Logout").click()

    def _test_assign_disk(self, name, diskname):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li/a", ["Assign disk"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li/a").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Select a disk to assign:"])

        driver.find_element_by_xpath("//div[@id='dialog-div']/form/div/fieldset/div/span[2]/a/span").click()
        driver.find_element_by_xpath("//a[contains(text(),'" + diskname + " (10 MB)')]").click()

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["Disk has been assigned."])

        driver.find_element_by_link_text("Logout").click()

    def _test_revoke_disk(self, name, diskname):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li[2]/a", ["Revoke disk"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr[7]/td/div/ul/li[2]/a").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Disk"])

        driver.find_element_by_xpath("//div[@id='dialog-div']/form/div/fieldset/div/span[2]/a/span").click()
        driver.find_element_by_xpath("//a[contains(text(),'" + diskname + "')]").click()

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["Disk has been revoked."])

        driver.find_element_by_link_text("Logout").click()

    def _test_monitoring(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[5]/a", ["Monitoring"])

        driver.find_element_by_link_text("Monitoring").click()

        self.wait_for_text("//form[@id='monitoring-form']/div[2]/div/ul/li", ["CPU time"])

        driver.get(self.base_url + "/vm/show_vm/")

        driver.find_element_by_link_text("Logout").click()

    def _test_assign_ip(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[13]/td[4]/ul/a", ["Assign"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr[13]/td[4]/ul/a").click()

        driver.find_element_by_xpath("//div[@id='dialog-div']/form/div/fieldset/div/span[2]/a/span").click()
        driver.find_element_by_xpath("//a[contains(text(),'.')]").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Select an IP address to assign:"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully assigned selected IP address."])

        driver.find_element_by_link_text("Logout").click()

    def _test_revoke_ip(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr[13]/td[4]/ul/a", ["."])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr[13]/td[4]/ul/a").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to revoke IP address"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully revoked IP address"])

        driver.find_element_by_link_text("Logout").click()

    def _test_destroy_multiple_vm(self, vm_list):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        for name in vm_list:
            self.wait_for_text("//table[@id='item-list']/tbody", [name])

            self.cell_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"}, "", "input")

        driver.find_element_by_xpath("//li[@id='group_action']/a").click()

        self.wait_for_text("//ul[@id='context-menu-list']/li", ["Destroy"])

        driver.find_element_by_xpath("//ul[@id='context-menu-list']/li[1]").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to destroy"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["successfully destroyed"])

        driver.find_element_by_link_text("Logout").click()

    def _test_edit_vm_description(self, name, description):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/vm/show_vm/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.row_click("Name", name, {"dict": {"State": "running"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[4]/a", ["Edit"])

        driver.find_element_by_xpath("//div[@id='vm_details']/div[5]/div/table/tbody/tr/td/div/ul/li[4]/a").click()

        self.wait_for_text("//span[@id='ui-dialog-title-dialog-div']", ["Edit virtual machine"])

        driver.find_element_by_xpath("//textarea[@id='id_description']").clear()
        driver.find_element_by_xpath("//textarea[@id='id_description']").send_keys(description)
        driver.find_element_by_xpath("//button[@type='submit']").click()

        self.wait_for_message(["You have successfully edited virtual machine data."])

        driver.find_element_by_link_text("Logout").click()

    def test_1_simple(self):
        name = self._test_create_vm(self)
        newname = self._test_edit_vm(name)
        self._test_enable_vnc(newname)
        self._test_disable_vnc(newname)
        self._test_destroy_vm(self, newname)

    def test_2_disks(self):
        diskname = resources_test.ResourcesTests._test_create_disk(self)
        name = self._test_create_vm(self)
        self._test_assign_disk(name, diskname)
        self._test_monitoring(name)
        self._test_reset_vm(name)
        self._test_revoke_disk(name, diskname)
        resources_test.ResourcesTests._test_remove_disk(self, diskname)
        self._test_destroy_vm(self, name)

    def test_3_simple(self):
        name = self._test_create_vm(self)
        resources_test.ResourcesTests._test_request_ip(self)
        self._test_assign_ip(name)
        self._test_revoke_ip(name)
        resources_test.ResourcesTests._test_release_ip(self)
        self._test_destroy_vm(self, name)

    def test_4_multiple_destroy(self):
        name = self._test_create_vm(self)
        name2 = self._test_create_vm(self)
        self._test_destroy_multiple_vm([name2, name])

    def test_5_utf8_check(self):
        name = self._test_create_vm(self)
        self._test_edit_vm_description(name, u'ąęł')
        self._test_destroy_vm(self, name)
