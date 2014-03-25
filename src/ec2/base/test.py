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

"""@package src.ec2.base.test
@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Oleksandr Gituliar <gituliar@gmail.com>
"""

import unittest

import mock


def trim(string):
    """Trim a multi-line string (the idea is taken from PEP 257)."""
    lines = string.splitlines()
    indent = 0
    while lines[1][indent] == ' ':
        indent += 1
    return lines[0] + '\n' + '\n'.join(line[indent:] for line in lines[1:])


class TestCase(unittest.TestCase):

    def assertMultiLineEqual(self, s1, s2, **kwargs):
        """Compare two multi-line strings disregarding indentation."""
        super(TestCase, self).assertMultiLineEqual(s1, trim(s2), **kwargs)

    def setUp(self):
        self.maxDiff = None
        self.patcher = mock.patch('restapi.ec2.main.ClusterManager')
        self.cluster_manager = self.patcher.start()
        self.cluster_manager.name = "test_cm"

    def tearDown(self):
        self.patcher.stop()
