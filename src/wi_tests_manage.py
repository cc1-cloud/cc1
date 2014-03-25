#!/usr/bin/env python2.7
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

"""@package src.wi.tests_manage

Control Interface for running CC1 Project's tests

Usage:
    manage.py runtest wi [--testserver=HOSTNAME] [--testfiles=TEST_FILES]
    manage.py --help

Options:
    --testserver=HOSTNAME    test server hostname ([host]:[port]). If not set local develompment server is started.
    --testfiles=TEST_FILES    which tests to run. Only test files that match the pattern will be loaded. (Using shell style pattern matching.)

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 25.10.2013
"""

import datetime
import docopt
import os
import sys

BASEDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASEDIR)


class Commands(object):
    """Manager that stores implementation of commands as Python functions."""

    COMMANDS = {}

    @classmethod
    def get_command(self, cmds):
        func = self.COMMANDS.get(tuple(sorted(list(cmds))))
        if not func:
            raise Exception("Unknown command '%s'" % cmds)
        return func

    @classmethod
    def set_command(self, func, *cmds):
        self.COMMANDS[tuple(sorted(list(cmds)))] = func


def runtest_wi(args):
    if args['--testserver'] is None:
        from django.core.management import execute_from_command_line
        from threading import Thread
        import time

        # load settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wi.settings")
        from django.conf import settings

        # edit wi settings to disable CAPTCHA
        settings.CAPTCHA = False

        # run local webserver
        server = Thread(target=execute_from_command_line, args=([[__file__, 'runserver', '--noreload']]))
        server.start()
        time.sleep(1)

    else:
        # set test server host
        from wi import tests
        tests.TEST_SERVER = args['--testserver']

    # load tests
    from unittest import TestLoader, TextTestRunner
    if args['--testfiles'] is None:
        print('Test file not specified.')
        test_files = '*test.py'
    else:
        test_files = args['--testfiles']

    print('Running tests: ' + test_files)
    tests = TestLoader().discover(os.path.join(BASEDIR, 'wi', 'tests'), test_files)

    # run and save result to file
    with open(os.path.join(os.path.dirname(__file__), 'wi', 'tests.log').replace('\\', '/'), 'w') as f:
        f.write('Test run ' + str(datetime.datetime.now()) + '\n\n')
        testResults = TextTestRunner(stream=f, verbosity=2).run(tests)
        print('Tests finished. Errors: ' + str(len(testResults.errors) + len(testResults.failures)) + '.')

Commands.set_command(runtest_wi, 'runtest', 'wi')

if __name__ == '__main__':
    options = docopt.docopt(__doc__, help=True)
    command, arguments = [], {}
    for arg, val in options.iteritems():
        if arg[0] == '-' or arg[0].isupper():
            arguments[arg] = val
        elif val:
            command.append(arg)
    func = Commands.get_command(command)
    func(arguments)
    exit(0)
