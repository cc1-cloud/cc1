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
"""@package src.wi.tests.resources_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 30.10.2012
"""

from wi.tests import WiTestCase
import cm_networks_test
import unittest
import random


class ResourcesTests(WiTestCase, unittest.TestCase):
    @staticmethod
    def _test_upload_iso(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/iso/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Upload ISO image"])

        driver.find_element_by_link_text("Upload ISO image").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Please specify ISO image parameters:"])

        name = "witest_iso" + str(random.randint(1, 100000))

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys(self.iso)
        driver.find_element_by_id("id_path").clear()
        driver.find_element_by_id("id_path").send_keys(self.iso)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["ISO image upload started."])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_edit_iso(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/iso/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/p", ["Edit ISO image data:"])

        newname = "new_witest_iso" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["ISO image data edited."])

        driver.find_element_by_link_text("Logout").click()

        return newname

    def _test_remove_iso(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/iso/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Remove")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you really want to delete ISO image"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully removed ISO image"])

        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_create_disk(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/disks/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Create new disk"])

        driver.find_element_by_link_text("Create new disk").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Specify disk properties:"])

        name = "witest_disk" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys("10 MB")
        driver.find_element_by_id("id_size").clear()
        driver.find_element_by_id("id_size").send_keys("10")
        driver.find_element_by_xpath("//form/div/fieldset/div[4]/span[2]/a/span").click()
        driver.find_element_by_xpath("//a[contains(text(),'" + "virtio" + "')]").click()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["Disk is being created."])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_upload_disk(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/disks/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Upload disk"])

        driver.find_element_by_link_text("Upload disk").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Please specify disk parameters:"])

        name = "witest_disk" + str(random.randint(1, 100000))

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys(self.iso)
        driver.find_element_by_id("id_path").clear()
        driver.find_element_by_id("id_path").send_keys(self.iso)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["Disk upload started."])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_edit_disk(self, name, newname):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/disks/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/p", ["Edit disk data"])

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited selected disk."])

        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_remove_disk(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/disks/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Remove", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you really want to delete disk volume"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully removed disk"])

        driver.find_element_by_link_text("Logout").click()

    def _test_request_network(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/networks/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Add a new network"])

        driver.find_element_by_link_text("Add a new network").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Network name"])

        name = "witest_network" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_mask").clear()
        driver.find_element_by_id("id_mask").send_keys("28")
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully added a network"])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_release_network(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/networks/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.cell_click("Name", name, element="a")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to release network"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully released network"])

        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_request_ip(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/elastic_ip/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Add a new IP"])

        driver.find_element_by_link_text("Add a new IP").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to add an IP address?"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["New IP address has been added."])

        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_release_ip(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/resources/elastic_ip/")

        self.wait_for_text("//table[@id='item-list']/tbody", ["not assigned"])

        self.cell_click("Attached to machine", "not assigned", element="a")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to release IP address"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["has been released."])

        driver.find_element_by_link_text("Logout").click()

    def test_1_simple_disk(self):
        name = self._test_create_disk(self)
        newname = "new_witest_disk" + str(random.randint(1, 100000))
        self._test_edit_disk(name, newname)
        self._test_remove_disk(self, newname)

    def test_2_simple_iso(self):
        name = self._test_upload_iso(self)
        newname = self._test_edit_iso(name)
        self._test_remove_iso(newname)

    def test_3_simple_network(self):
        cm_networks_test.CMNetworksTests._test_add_pool(self)
        name = self._test_request_network()
        self._test_release_network(name)
        cm_networks_test.CMNetworksTests._test_delete_pool(self)

    def test_4_simple_ip(self):
        self._test_request_ip(self)
        self._test_release_ip(self)

    def test_5_utf8_edit(self):
        name = self._test_create_disk(self)
        newname = u'ąłęćĄŁ'
        self._test_edit_disk(name, newname)
        self._test_remove_disk(self, newname)

    def test_6_upload_disk(self):
        name = self._test_upload_disk()
        self._test_remove_disk(self, name)
