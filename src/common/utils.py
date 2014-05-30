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
import subprocess
import sys
import shlex

"""@package src.common.utils
"""

import datetime
import json
import logging
import os
import random
import re
import requests
import string
import xml.sax.handler


def xml2dict(src):
    """
    A simple function to converts XML data into native Python dictionary.

    @parameter{src} xml file content or stream
    """

    non_id_char = re.compile('[^_0-9a-zA-Z]')

    def _name_mangle(name):
        return non_id_char.sub('_', name)

    def add_attr(data, name, value):
        """
        Adds to @prm{data} dictionary key named @prm{name} with value
        @prm{value}. If @prm{name} key with single-value already exists
        in @prm{data} key, it's converted into list. If it's already
        converted into list, yet another value is added.
        @parameter{data,dict} to which dictionary key should be added
        @parameter{name,string} name of the key
        @parameter{value,string} value of the key
        """
        if name in data.keys():
            # multiple attribute of the same name are represented by a list
            children = data[name]
            if not isinstance(children, list):
                children = [children]
                data[name] = children
            children.append(value)
        else:
            data[name] = value

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = {}
            self.current = self.root
            self.text_parts = []

        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = {}
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                add_attr(self.current, _name_mangle(k), v)

        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current['text'] = text
            if self.current:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            add_attr(self.current, _name_mangle(name), obj)

        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src, basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root


def ip_itos(ip_int):
    """
    Convert ip from long-integer to standard, human-readable form.
    """
    ip = []
    ip.append(str((ip_int & 0xFF000000L) >> 24))
    ip.append(str((ip_int & 0x00FF0000L) >> 16))
    ip.append(str((ip_int & 0x0000FF00L) >> 8))
    ip.append(str(ip_int & 0x000000FFL))
    return '.'.join(ip)


def ip_stoi(ip):
    """
    Convert ip from human-readable form to long-integer.
    @parameter{ip,string} IP address with 4 dot-separated numbers (0-255).
    @returns{long int} number representation of the given @prm{ip}
    """
    bins = ip.split('.')
    return long(bins[0]) << 24 | int(bins[1]) << 16 | int(bins[2]) << 8 | int(bins[3])


def ip_stomac(ip):
    """
    Convert ip from string to mac address.
    @parameter{ip,string} IP address with 4 dot-separated numbers (0-255).
    @returns{string} mac address
    """
    return '02:00:%02x:%02x:%02x:%02x' % tuple([int(x) for x in ip.split('.')])


def password_gen(length, chars=['letters', 'digits', 'special'], extra_chars=None):
    """
    Generates random password of given length. The password consists
    of symbols drawn from the set of specified character groups (@prm{chars})
    and (optionally) of extra characters specified in (@prm{extra_chars}).
    @parameter{length,int} length of the requested password
    @parameter{chars,list(string)} may contain @str{letters}, @str{digits}, or
    @str{special}.
    @parameter{extra_chars,list(char)} list of extra characters for password
    composition.
    @returns{string} password composed of @prm{length} symbols picked from
    specified character set
    """
    pool = ''
    if 'letters' in chars:
        pool += string.ascii_letters
    if 'digits' in chars:
        pool += string.digits
    if 'special' in chars:
        pool += string.punctuation
    if extra_chars:
        pool += extra_chars

    seen = set()
    pool = [x for x in pool if x not in seen and not seen.add(x)]

    random.seed = (os.urandom(1024))
    return ''.join(random.choice(pool) for i in range(length))


def json_convert(o):
    """
    Convert object to json format
    """

    DATE_FORMAT = "%d.%m.%Y"
    TIME_FORMAT = "%H:%M:%S"

    if type(o) == datetime.date:
        return o.strftime(DATE_FORMAT)
    elif type(o) == datetime.time:
        return o.strftime(TIME_FORMAT)
    elif type(o) == datetime.datetime:
        return o.strftime("%s, %s" % (DATE_FORMAT, TIME_FORMAT))
    else:
        return json.dumps(o)


class ServerProxy(object):
    def __init__(self, server_address):
        self.server_address = server_address

    def send_request(self, url, log=True, **data):
        logger = logging.getLogger('request')
        data = json.dumps(data, default=json_convert)
        if log:
            logger.info("called %s/%s   body: %s" % (self.server_address, url, data))

        response = requests.post("%s/%s" % (self.server_address, url), data=data)

        if not response.ok:
            logger.error("HTTP ERROR: code: %s data: %s" % (response.status_code, response.text[:100]))
            raise Exception("Status %s failed to call function" % response.status_code)
        response = json.loads(response.text)
        if log:
            logger.info("response from %s/%s is:\n%s" % (self.server_address, url, json.dumps(response, indent=4)))
        if not isinstance(response, dict):
            logger.error("Returned object is %s expected dict. Data: %s" % (type(response), response))
            raise Exception("Returned object is %s expected dict" % type(response))
        if 'status' not in response or 'data' not in response:
            logger.error("Returned object is malformatted: %s" % response)
            raise Exception("Returned object is malformatted: %s" % response)
        return response


def subcall(command, log=None, err_log=None, std_log=None, err_msg=None, err_exit=True):
    if not (std_log or err_log):
        std_log = log
        err_log = log
    r = subprocess.call(command, shell=True, stdout=std_log, stderr=err_log)
    if r > 0:
        if err_msg:
            START_MSG = '\033[91m' if err_exit else '\033[93m'
            END_MSG = '\033[0m'
            print "%s%s%s" % (START_MSG, err_msg, END_MSG)
        if err_exit:
            sys.exit(1)
    return r
