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
"""@package src.wi.tests.test_clean
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 20.02.2013
"""

from wi.tests import WiTestCase
import cm_images_test
import unittest


class CleanTests(WiTestCase, unittest.TestCase):
    def _test_erase_vms(self, search_text):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        self.login_cm_testuser()

        driver.get(self.base_url + "/admin_cm/vms/")

        driver.find_element_by_xpath("//div[@id='searchBox']/input").clear()
        driver.find_element_by_xpath("//div[@id='searchBox']/input").send_keys(search_text)

        if self.wait_for_text("//table[@id='item-list']/tbody", [search_text], fail=False) == False:
            driver.find_element_by_link_text("Logout from CM").click()
            driver.find_element_by_link_text("Logout").click()
            return False

        driver.find_element_by_id("auto-refresh").click()

        driver.find_element_by_xpath("//table[@id='item-list']/thead/tr/td/input").click()

        driver.find_element_by_xpath("//li[@id='group_action']/a").click()

        self.wait_for_text("//ul[@id='context-menu-list']/li", ["Erase"])

        driver.find_element_by_xpath("//ul[@id='context-menu-list']/li[2]").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to erase"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["successfully erased"])

        driver.find_element_by_link_text("Logout from CM").click()
        driver.find_element_by_link_text("Logout").click()

    def test_clean_images(self):
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_image(self, 'witest_image', fail=False)
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_image(self, 'witest_cm_image', fail=False)
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_image(self, 'failed', column='State', fail=False)
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_image(self, 'adding', column='State', fail=False)

    def test_clean_isos(self):
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_iso(self, 'witest_iso', fail=False)
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_iso(self, 'failed', column='Size', fail=False)
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_iso(self, '%', column='Size', fail=False)

    def test_clean_disks(self):
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_disk(self, 'witest_disk', fail=False)
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_disk(self, 'failed', column='Size', fail=False)
        resp = True
        while(resp):
            resp = cm_images_test.CMImagesTests._test_remove_disk(self, '%', column='Size', fail=False)

    def test_clean_vms(self):
        self._test_erase_vms('failed')
        self._test_erase_vms('witest_vm')
