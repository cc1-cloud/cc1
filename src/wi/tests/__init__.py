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
"""@package src.wi.tests

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 11.10.2012
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import re
import time

TEST_SERVER = 'localhost:8000'


class WiTestCase:
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(20)
        self.TEST_USER = {'login': 'test_user', 'password': 'test1'}
        self.TEST_admin_cm = {'login': 'test_cmadmin', 'password': 'test1', 'cm_password': 'test1'}
        self.TEST_SERVER = TEST_SERVER
        self.iso = "http://archive.ubuntu.com/ubuntu/dists/quantal/main/installer-i386/current/images/netboot/mini.iso"

    def tearDown(self):
        self.driver.quit()

    def wait_for_text(self, xpath, text_list, max_time=20, sleep_time=0.5, fail=True):
        """
        @parameter{xpath,string} xpath in which text should appears
        @parameter{text_list,list} list containing possible texts
        @parameter{max_time,int} describes how long method should search for text
        @parameter{sleep_time,double} describes gaps between consecutive searches
        @parameter{fail,boolean} describes if failure should brake test case

        Checks if one of texts has appeared in described xpath.
        """
        end_time = time.time() + max_time
        while(True):
            try:
                el = self.driver.find_elements_by_xpath(xpath)
                for text in text_list:
                    if text in "".join(i.text for i in el):
                        return True
            except NoSuchElementException:
                return False

            time.sleep(sleep_time)
            if(time.time() > end_time):
                break
        if fail == False:
            return False
        self.fail("time out while searching for \"" + text + "\"")

    def wait_for_message(self, text_list, max_time=20, sleep_time=0.5):
        """
        @parameter{text_list,list} is list containing possible texts
        @parameter{max_time,int} describes how long method should search for text
        @parameter{sleep_time,double} describes gaps between consecutive searches

        Checks if message with described text appears on the page
        """
        end_time = time.time() + max_time
        while(True):
            try:
                el = self.driver.find_elements_by_xpath("//div[@id='top-messages']/div")
                for i in el:
                    if i.get_attribute("class") == "error":
                        i.find_element(By.CLASS_NAME, "remove-button").click()
                        self.fail(i.text)

                for text in text_list:
                    if text in "".join(i.text for i in el):
                        return True
            except NoSuchElementException:
                return False

            time.sleep(sleep_time)
            if(time.time() > end_time):
                break
        self.fail("time out while seraching for \"" + text + "\"")

    def __wait_for_table_update(self, col_name, text, check_data,
                                path_body_trs, path_head_tds, max_time=100, sleep_time=5):
        """
        @parameter{col_name,string} name of column in which text should appear
        @parameter{text,string} text
        @parameter{path_body_trs,string} xpath for searching rows of table
        @parameter{path_head_tds,string} xpath for searching head's cells of table
        @parameter{max_time,int} describes how long method should search for text
        @parameter{sleep_time,double} describes gaps between consecutive searches
        @parameter{check_data,dict}
        \n fields:
        @dictkey{path,string} path of table
        @dictkey{dict,dict} contains pairs: *col name* and *text* which are additional requirements for searched row

        Searchs for row in table and checks if it meets additional requirements described in check_data
        if not wait for table refresh and checks again
        """

        end_time = time.time() + max_time
        while(True):
            ind_col = self.__get_index_of_column(col_name, path_head_tds)
            row = self.__find_row(ind_col, text, path_body_trs)
            self.assertNotEqual(row, None, "Didn't find text %s in column %s" % (text, col_name))

            checked = True
            for key, value in check_data['dict'].iteritems():
                ind_key = self.__get_index_of_column(key, path_head_tds)
                if not value in row[ind_key].text:
                    checked = False
            if checked:
                return True

            time.sleep(sleep_time)
            if(time.time() > end_time):
                break

            self.driver.refresh()
            self.wait_for_text(check_data['path'], [text])

            el = self.driver.find_elements_by_xpath("//div[@id='top-messages']/div")
            for i in el:
                if i.get_attribute("class") == "error":
                    i.find_element(By.CLASS_NAME, "remove-button").click()
                    self.fail(i.text)

        self.fail("time out while seraching for \"" + text + "\"")

    def __get_index_of_column(self, col_name, path_head_tds):
        """
        @parameter{col_name,string} name of column
        @parameter{path_head_tds,string} xpath for searching head's cells of table

        Return index of column
        """
        ind_col = -1

        tds = self.driver.find_elements_by_xpath(path_head_tds)
        for i in range(len(tds)):
            td = tds[i]
            if td.text == col_name:
                ind_col = i

        self.assertNotEqual(ind_col, -1, "Column not found: %s" % (col_name))

        return ind_col

    def __find_row(self, ind_col, text, path_body_trs):
        """
        @parameter{ind_col,int} index of column
        @parameter{text,string} text
        @parameter{path_body_trs,string} xpath for searching rows of table

        Return tds of row in which text appears in described column
        """
        trs = self.driver.find_elements_by_xpath(path_body_trs)

        for i in range(len(trs)):
            tds = trs[i].find_elements(By.TAG_NAME, "td")
            if len(tds) > ind_col:
                if text in tds[ind_col].text:
                    return tds

        return None

    def __click_menu_item(self, menu_item_text):
        """
        @parameter{menu_item_text,string}

        Clicks on item in context menu
        """

        self.wait_for_text("//ul[@id='context-menu-list']/li", [menu_item_text])
        items = self.driver.find_elements_by_xpath("//ul[@id='context-menu-list']/li")
        for i in items:
            if i.text == menu_item_text:
                i.click()
                return

    def cell_click(self, col_name, text, check_data=None, action_name="Actions", element="div",
                    path_head_tds="//table[@id='item-list']/thead/tr/td",
                    path_body_trs="//table[@id='item-list']/tbody/tr"):
        """
        @parameter{col_name,string} name of column which together with text describe row
        @parameter{text,string} text
        @parameter{action_name,string} name of column which together with row describes cell
        @parameter{element,string} element in cell which sholud be clicked
        @parameter{path_body_trs,string} xpath for searching rows of table
        @parameter{path_head_tds,string} xpath for searching head's cells of table
        @parameter{max_time,int} describes how long method should search for text
        @parameter{sleep_time,double} describes gaps between consecutive searches
        @parameter{check_data,dict}
        \n fields:
        @dictkey{path,string} path of table
        @dictkey{dict,dict} contains pairs: *col name* and *text* which are additional requirements for searched row

        Clicks on cell described by parameters
        """

        if check_data != None:
            self.__wait_for_table_update(col_name, text, check_data, path_body_trs, path_head_tds)

        ind_col = self.__get_index_of_column(col_name, path_head_tds)
        row = self.__find_row(ind_col, text, path_body_trs)
        self.assertNotEqual(row, None, "Didn't find text %s in column %s" % (text, col_name))

        ind_action = self.__get_index_of_column(action_name, path_head_tds)

        row[ind_action].find_element(By.TAG_NAME, element).click()

    def row_click(self, col_name, text, check_data=None,
                  path_head_tds="//table[@id='item-list']/thead/tr/td",
                  path_body_trs="//table[@id='item-list']/tbody/tr"):
        """
        @parameter{col_name,string} name of column which together with text describe row
        @parameter{text,string} text
        @parameter{path_body_trs,string} xpath for searching rows of table
        @parameter{path_head_tds,string} xpath for searching head's cells of table
        @parameter{check_data,dict}
        \n fields:
        @dictkey{path,string} path of table
        @dictkey{dict,dict} contains pairs: *col name* and *text* which are additional requirements for searched row

        Clicks on row described by parameters
        """
        if check_data:
            self.__wait_for_table_update(col_name, text, check_data, path_body_trs, path_head_tds)

        ind_col = self.__get_index_of_column(col_name, path_head_tds)
        row = self.__find_row(ind_col, text, path_body_trs)
        self.assertNotEqual(row, None, "Didn't find text %s in column %s" % (text, col_name))

        row[ind_col].click()

    def menu_click(self, col_name, text, menu_item_text, check_data=None, action_name="Actions"):
        """
        @parameter{col_name,string} name of column which together with text describe row
        @parameter{text,string} text
        @parameter{action_name,string} name of column which together with row describe cell
        @parameter{menu_item_text,string} xpath for searching rows of table
        @parameter{check_data,dict}
        \n fields:
        @dictkey{path,string} path of table
        @dictkey{dict,dict} contains pairs: *col name* and *text* which are additional requirements for searched row

        Clicks on cell described by parameters and then clicks on item in context menu
        """

        self.cell_click(col_name, text, check_data, action_name)
        self.__click_menu_item(menu_item_text)

    def login_testuser(self, user):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        driver.get(self.base_url + '/auth/login/')

        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys(user['login'])
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys(user['password'])
        driver.find_element_by_css_selector("input.big_button").click()

        self.wait_for_text("//div[@id='header']/ul/li", ["test"])
        self.change_language()

    def login_cm_testuser(self):
        driver = self.driver
        self.base_url = self.TEST_SERVER

        driver.get(self.base_url + '/admin_cm/login/')

        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys(self.TEST_admin_cm['cm_password'])
        driver.find_element_by_css_selector("input.big_button").click()

        self.wait_for_text("//div[@id='header']/ul/li", ["test"])
        self.change_language()

    def change_language(self):
        driver = self.driver
        driver.find_element_by_xpath("//form[@id='languageForm']/a/span[2]").click()
        driver.find_element_by_xpath("//a[contains(text(),'English')]").click()
