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
"""@package src.wi.tests.farm_test
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 24.05.2013
"""

from wi.tests import WiTestCase
import random
import resources_test
import unittest


class FarmTests(WiTestCase, unittest.TestCase):
    def _test_create_farm(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/farm/create_farm/")

        self.wait_for_text("//div[@id='item-list']/div[2]/table/tbody", ["witest_complete_ctx"])

        self.cell_click("Name", "witest_complete_ctx", None, element="a",
                         path_head_tds="//div[@id='item-list']/div[1]/table/tbody/tr/td",
                         path_body_trs="//div[@id='item-list']/div[2]/table/tbody/tr")

        self.wait_for_text("//form[@id='wizard-form']/div[2]/fieldset/div/span/label", ["Head template"])

        driver.find_element_by_xpath("//form[@id='wizard-form']/div[2]/fieldset/div/span[2]/a/span").click()
        driver.find_element_by_xpath("//a[contains(text(),'" + "small" + "')]").click()
        driver.find_element_by_xpath("//form[@id='wizard-form']/div[2]/fieldset/div[2]/span[2]/a/span").click()
        driver.find_elements_by_xpath("//a[contains(text(),'" + "small" + "')]")[1].click()

        driver.find_element_by_xpath("//div[@id='submit-div']/input").click()

        self.wait_for_text("//form[@id='wizard-form']/div[2]/fieldset/div/span/label", ["Assign IP address"])

        driver.find_element_by_xpath("//div[@id='submit-div']/input").click()

        self.wait_for_text("//form[@id='wizard-form']/div[2]/fieldset/div/span/label", ["Name"])

        name = "witest_farm" + str(random.randint(1, 100000))
        driver.find_element_by_id("id_3-name").clear()
        driver.find_element_by_id("id_3-name").send_keys(name)

        driver.find_element_by_css_selector("input.big_button").click()

        self.wait_for_message(["Farm is being created."])

        driver.find_element_by_link_text("Logout").click()

        return name

    def _test_destroy_farm(self, name):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_USER)

        driver.get(self.base_url + "/farm/show_farm/")

        self.wait_for_text("//div[@id='item-list']", [name])

        number = 0

        els = driver.find_elements_by_xpath("//div[@id='item-list']/div/h3")
        for i in range(len(els)):
            if name in els[i].text:
                number = i + 1
                break
        if number == 0:
            self.fail("time out while searching for \"" + name + "\"")

        self.wait_for_text("//div[@id='item-list']/div[" + str(number) + "]", ["Running"], max_time=100, sleep_time=5)

        driver.find_element_by_xpath("//div[@id='item-list']/div[" + str(number) + "]/table/tbody/tr/td/div/ul/li/a").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you really want to destroy farm"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully destroyed farm"])

        driver.find_element_by_link_text("Logout").click()

    def test_1_simple(self):
        name = self._test_create_farm()
        self._test_destroy_farm(name)
