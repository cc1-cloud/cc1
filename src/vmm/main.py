#!/usr/bin/python
# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @COPYRIGHT_end

from select import select
import json
import logging
import os
import requests
import settings
import sys
import time
from threading import Thread
import Input

APP_PATH = os.path.abspath(os.path.dirname(__file__))

# config loggers
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)

fh = logging.FileHandler(os.path.join(settings.LOG_DIR, 'vmm.log'))
fh.setLevel(settings.LOG_LEVEL)
logger.addHandler(fh)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(settings.LOG_LEVEL)
logger.addHandler(ch)

dev = Input.EventDevice()
try:
    dev.find(name="keyboard")
except Exception:
    raise Exception("No such device")
print dev
logger.info('Setting keyboard to %s bus=0x%x, vendor=0x%x, product=0x%x, version=0x%x' % (dev.name, dev.idbus, dev.idvendor, dev.idproduct, dev.idversion))



verify = os.path.isdir(settings.CA_DIR)

VERSION = 0
actions = None
try:
    actions = __import__('actions')
    VERSION = actions.VERSION
except Exception:
    pass


def rpc(cmd, params=None):
    logger.debug("RPC: %s, PARAMS: %s" % (cmd, params))
    global VERSION
    global actions
    if params:
        params['version'] = VERSION
    else:
        params = {'version': VERSION}
    try:
        r = requests.get('%s/%s' % (settings.CTX_ADDRESS, cmd), verify=verify, params=params)
        logger.debug('status: %s, ok: %s, text: %s' % (r.status_code, r.ok, r.text))
    except Exception, e:
        logger.error('requests error %s' % e)
        return

    if not r.ok:
        return

    r = json.loads(r.text)
    if not r:
        return None
    if r['status'] != 'ok':
        logger.error('RPC Error: %s' % r['status'])
    if 'actions_file' in r:
        f = file(os.path.join(APP_PATH, 'actions.py'), 'w')
        f.write(r['actions_file'])
        f.close()
        if 'actions' in sys.modules:
            reload(actions)
        else:
            
            actions = __import__('actions')
            VERSION = actions.VERSION
    return r


def gather_certs():
    ca_bundle = open('ca_bundle.crt', 'wb')

    if not os.path.isdir(settings.CA_DIR):
        logger.info('certificates directory does not exits, every request will be accepted')
        verify = False
        return
    for crt in os.listdir(settings.CA_DIR):
        f = open(os.path.join(settings.CA_DIR, crt), 'r')
        ca_bundle.writelines(f.readlines())


class HelloCommand(Thread):
    def run(self):
        gather_certs()
        ok = False
        fails = 10
        while not ok:
            try:
                r = rpc('hello')
                if r['status'] != 'ok':
                    logger.error('Hello failed, no acceptance from server (err %s), exiting program...' % (r['status']))
                    fails -= 1
                    if fails < 1:
                        exit(1)
                    #exit(1)
                else:
                    ok = True
            except Exception, e:
                logger.error('error while connecting to ctx server (will renew...) %s' % (e))
                time.sleep(60)


class ProcessCommand(Thread):
    def run(self):
        logger.info('Start thread')
        exist = True
        while exist:
            try:
                r = rpc('get_command')
                if not r or r['status'] != 'ok':
                    exist = False
                    break

                r = r['data']
                response = None
                command_id = r['id']
                logger.info("Requested command: %s(%s)" % (r['name'], r['args']))

                if 'name' not in r:
                    error_msg = 'ERROR: No command parameter'
                    logger.error(error_msg)
                    rpc('finish_command', {'status': 'failed', 'command_id': command_id,
                                           'error_message': error_msg})
                try:
                    call_action = getattr(actions, r['name'], None)
                    if not call_action:
                        rpc('finish_command', {'status': 'failed', 'command_id': command_id,
                                               'error_message': 'Invalid action'})
                    if r['args']:
                        args = json.loads(r['args'])
                    else:
                        args = {}
                    response = call_action(**args)
                    logger.info("response: %s" % str(response))
                    rpc('finish_command', dict({'status': 'finished', 'command_id': command_id, 'returns': response}))
                except Exception, e:
                    error_msg = 'ERROR: UNDEFINED ERROR %s' % unicode(e)
                    logger.exception(error_msg)
                    rpc('finish_command', {'status': 'failed', 'command_id': command_id,
                                           'error_message': error_msg})
            except Exception, e:
                logger.exception('General exception: %s' % e)
                exist = False

t = HelloCommand()
t.start()
# check if commands are in CM
t = ProcessCommand()
t.start()

logger.info('Waiting for keyboard')
while True:
    r, w, x = select([dev], [], [])
    for event in dev.readall():
        if event.code == 113 and event.value == 1:
            logger.info("Key received")
            t = ProcessCommand()
            t.start()
