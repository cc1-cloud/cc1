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
"""@package src.wi.tests.images_test
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 24.11.2012
"""

from wi.tests import WiTestCase
import groups_test
import vm_test
import unittest
import random


class ImagesTests(WiTestCase, unittest.TestCase):

    @staticmethod
    def _test_upload_image_private(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/images/images_private/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Upload image"])

        driver.find_element_by_link_text("Upload image").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Please specify image parameters:"])

        name = "witest_image" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys(self.iso)
        driver.find_element_by_id("id_path").clear()
        driver.find_element_by_id("id_path").send_keys(self.iso)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["Image upload started."])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_edit_image_private(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/images/images_private/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/p", ["Edit image data"])

        newname = "new_witest_image" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited this image."])

        driver.find_element_by_link_text("Logout").click()

        return newname

    @staticmethod
    def _test_remove_image_private(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/images/images_private/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Remove")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you really want to delete image"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully removed image"])

        driver.find_element_by_link_text("Logout").click()

    def _test_create_vm_from_image(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/images/images_private/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Create virtual machine", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

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

    def _test_group_image_private(self, name, group_name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/images/images_private/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Assign to group", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/p", ["Enter a name of group for image"])

        driver.find_element_by_xpath("//div[@id='dialog-div']/form/div/fieldset/div/span[2]/a/span").click()
        driver.find_element_by_xpath("//a[contains(text(),'" + group_name + "')]").click()

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully assigned image "])

        driver.find_element_by_link_text("Logout").click()

    def _test_ungroup_image_private(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/images/images_private/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Move to my images")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to make image"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully revoked group's assigment."])

        driver.find_element_by_link_text("Logout").click()

    def test_1_simple(self):
        name = self._test_upload_image_private(self)
        newname = self._test_edit_image_private(name)
        self._test_remove_image_private(self, newname)

    def test_2_create_vm(self):
        name = self._test_upload_image_private(self)
        vmname = self._test_create_vm_from_image(name)
        vm_test.VMTests._test_destroy_vm(self, vmname)
        self._test_remove_image_private(self, name)

    def test_3_group(self):
        name = self._test_upload_image_private(self)
        group_name = groups_test.GroupsTests._test_create_group(self)
        self._test_group_image_private(name, group_name)
        self._test_ungroup_image_private(name)
        groups_test.GroupsTests._test_remove_group(self, group_name, who=self.TEST_USER)
        self._test_remove_image_private(self, name)
