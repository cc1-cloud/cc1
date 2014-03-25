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
"""@package src.wi.tests.cm_images_test
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 09.01.2013
"""

from wi.tests import WiTestCase
import images_test
import random
import resources_test
import unittest


class CMImagesTests(WiTestCase, unittest.TestCase):

    def _test_register_image(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Register image"])

        driver.find_element_by_link_text("Register image").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        name = "witest_cm_image" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(name)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys(self.iso)
        driver.find_element_by_id("id_path").clear()
        driver.find_element_by_id("id_path").send_keys(self.iso)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully added an image."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_register_image_empty(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        self.wait_for_text("//table[@id='item-list']/tfoot/tr/td/ul/li/a", ["Register image"])

        driver.find_element_by_link_text("Register image").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_path").clear()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/ul/li", ["This field is required."])
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset[2]/div[2]/ul/li", ["This field is required."])
        driver.find_element_by_css_selector("button.cancel-button.mid_button").click()

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_edit_image(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        newname = "new_witest_cm_image" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited selected image."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        return newname

    def _test_edit_image_empty(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Name"])

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/ul/li", ["This field is required."])
        driver.find_element_by_css_selector("button.cancel-button.mid_button").click()

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_copy_image(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Copy", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["User"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["copied."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_remove_image(self, name, fail=True, column="Name"):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        if self.wait_for_text("//table[@id='item-list']/tbody", [name], fail=fail) == False:
            driver.find_element_by_link_text("Logout from CM").click()
            driver.find_element_by_link_text("Logout").click()
            return False

        self.menu_click(column, name, "Remove")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to delete image"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully deleted image"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        if fail == False:
            return True

    def _test_public_image(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Move to public images", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to make image"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully changed type of image"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_private_image(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/images/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Move to private images", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to make image"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully changed type of image"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_edit_disk(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/disks/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Disk name"])

        newname = "new_witest_disk" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited selected disk."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        return newname

    def _test_edit_disk_empty(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/disks/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["Disk name"])

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/ul/li", ["This field is required."])
        driver.find_element_by_css_selector("button.cancel-button.mid_button").click()

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_copy_disk(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/disks/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Copy", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["User"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["copied."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_remove_disk(self, name, column="Name", fail=True):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/disks/")

        if self.wait_for_text("//table[@id='item-list']/tbody", [name], fail=fail) == False:
            driver.find_element_by_link_text("Logout from CM").click()
            driver.find_element_by_link_text("Logout").click()
            return False

        self.menu_click(column, name, "Remove")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to delete disk"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully removed disk volume"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        if fail == False:
            return True

    def _test_edit_iso(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/iso/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["ISO image name"])

        newname = "new_witest_iso" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys(newname)
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully edited selected ISO image."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        return newname

    def _test_edit_iso_empty(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/iso/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Edit", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["ISO image name"])

        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()
        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/ul/li", ["This field is required."])
        driver.find_element_by_css_selector("button.cancel-button.mid_button").click()

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def _test_copy_iso(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/iso/")

        self.wait_for_text("//table[@id='item-list']/tbody", [name])

        self.menu_click("Name", name, "Copy", {"dict": {"Size": "B"}, "path": "//table[@id='item-list']/tbody"})

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span/label", ["User"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["copied."])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    @staticmethod
    def _test_remove_iso(self, name, column="Name", fail=True):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/iso/")

        if self.wait_for_text("//table[@id='item-list']/tbody", [name], fail=fail) == False:
            driver.find_element_by_link_text("Logout from CM").click()
            driver.find_element_by_link_text("Logout").click()
            return False

        self.menu_click(column, name, "Remove")

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to delete ISO image"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully deleted ISO image"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

        if fail == False:
            return True

    def test_1_simple(self):
        name = self._test_register_image()
        newname = self._test_edit_image(name)
        self._test_copy_image(newname)
        self._test_remove_image(self, newname)

    def test_2_simple(self):
        name = images_test.ImagesTests._test_upload_image_private(self)
        newname = self._test_edit_image(name)
        self._test_copy_image(newname)
        self._test_remove_image(self, newname)
        self._test_remove_image(self, newname)

    def test_3_change_type(self):
        name = self._test_register_image()
        self._test_public_image(name)
        self._test_private_image(name)
        self._test_remove_image(self, name)

    def test_4_simple_disk(self):
        name = resources_test.ResourcesTests._test_create_disk(self)
        newname = self._test_edit_disk(name)
        self._test_copy_disk(newname)
        self._test_remove_disk(self, newname)
        self._test_remove_disk(self, newname)

    def test_5_simple_iso(self):
        name = resources_test.ResourcesTests._test_upload_iso(self)
        newname = self._test_edit_iso(name)
        self._test_copy_iso(newname)
        self._test_remove_iso(self, newname)
        self._test_remove_iso(self, newname)

    def test_6_register_image_errors(self):
        self._test_register_image_empty()

    def test_7_edit_image_errors(self):
        name = self._test_register_image()
        self._test_edit_image_empty(name)
        self._test_remove_image(self, name)

    def test_8_edit_disk_errors(self):
        name = resources_test.ResourcesTests._test_create_disk(self)
        self._test_edit_disk_empty(name)
        self._test_remove_disk(self, name)

    def test_9_edit_iso_errors(self):
        name = resources_test.ResourcesTests._test_upload_iso(self)
        self._test_edit_iso_empty(name)
        self._test_remove_iso(self, name)
