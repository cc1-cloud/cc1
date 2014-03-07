#!/usr/bin/env python
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
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage ./manage.py <manager> <args>'
        sys.exit(1)

    # cc1dir = os.path.abspath(os.path.dirname(__file__))
    # sys.path.append(os.path.join(cc1dir, sys.argv[1]))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % sys.argv[1])

    from django.core.management import execute_from_command_line
    args = sys.argv[:]
    args.pop(1)

    execute_from_command_line(args)
