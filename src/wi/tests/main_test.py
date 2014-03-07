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
"""@package src.wi.tests.main_test

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 11.10.2012
"""

from wi.tests import WiTestCase
import unittest


class MainTests(WiTestCase, unittest.TestCase):
    def _test_news_create(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        driver.get(self.base_url + "/news/")

        self.wait_for_text("//a[@id='main_create_news']", ["Create a news entry"])

        driver.find_element_by_id("main_create_news").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Topic"])

        driver.find_element_by_id("id_topic").clear()
        driver.find_element_by_id("id_topic").send_keys("witest")
        driver.find_element_by_id("id_content").clear()
        driver.find_element_by_id("id_content").send_keys("test")
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["News entry added."])

        driver.find_element_by_link_text("Logout").click()

    def _test_news_create_fail_required(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        driver.get(self.base_url + "/news/")

        self.wait_for_text("//a[@id='main_create_news']", ["Create a news entry"])

        driver.find_element_by_id("main_create_news").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Topic"])

        driver.find_element_by_id("id_topic").clear()
        driver.find_element_by_id("id_content").clear()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div[1]/ul/li", ["This field is required."])

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div[2]/ul/li", ["This field is required."])

        driver.find_element_by_link_text("Logout").click()

    def _test_news_create_sticky(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        driver.get(self.base_url + "/news/")

        self.wait_for_text("//a[@id='main_create_news']", ["Create a news entry"])

        driver.find_element_by_id("main_create_news").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Topic"])

        driver.find_element_by_id("id_topic").clear()
        driver.find_element_by_id("id_topic").send_keys("witest")
        driver.find_element_by_id("id_content").clear()
        driver.find_element_by_id("id_content").send_keys("test")
        driver.find_element_by_id("id_sticky").click()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["News entry added."])

        driver.find_element_by_link_text("Logout").click()

    def _test_news_edit(self, topic):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        driver.get(self.base_url + "/news/")

        self.wait_for_text("//div[@id='item-list']/div/div[2]", ["witest"])

        driver.find_element_by_id("main_edit_news").click()

        self.wait_for_text("//div[@id='dialog-div']/form/div/fieldset/div/span", ["Topic"])

        driver.find_element_by_id("id_topic").clear()
        driver.find_element_by_id("id_topic").send_keys(topic)
        driver.find_element_by_id("id_content").clear()
        driver.find_element_by_id("id_content").send_keys("test2")
        driver.find_element_by_id("id_sticky").click()
        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["News entry edited."])

        driver.find_element_by_link_text("Logout").click()

    def _test_news_remove(self, topic):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        self.login_testuser(self.TEST_admin_cm)
        driver.get(self.base_url + "/news/")

        self.wait_for_text("//div[@id='item-list']/div/div[2]", [topic])

        driver.find_element_by_id("main_remove_news").click()

        self.wait_for_text("//div[@id='dialog-div']/p", ["Do you want to delete news entry"])

        driver.find_element_by_css_selector("button.ok-button.mid_button").click()

        self.wait_for_message(["You have successfully removed news entry"])

        driver.find_element_by_link_text("Logout").click()

    def test_1_simple(self):
        self._test_news_create()
        topic = 'witest'
        self._test_news_edit(topic)
        self._test_news_remove(topic)

    def test_2_fails(self):
        self._test_news_create_fail_required()

    def test_3_utf8_edit(self):
        self._test_news_create()
        topic = u'ąśłęąĄŁŁ'
        self._test_news_edit(topic)
        self._test_news_remove(topic)
