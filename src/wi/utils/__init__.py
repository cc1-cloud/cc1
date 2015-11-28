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

"""@package src.wi.utils

@author Piotr Wójcik
@date 24.03.2011
"""

import logging
import os
from time import time

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from common.utils import ServerProxy
from wi.utils.exceptions import RestErrorException
from wi.utils.messages_ajax import error, success
from wi.utils.messages_codes import get_error, auth_error_text


REDIRECT_FIELD_NAME = 'next'
CLM = ServerProxy(settings.CLOUD_MANAGER_ADDRESS)


def check_response_errors(response, session):
    """
    Checks status of response response and throws appropriate error.
    """
    if response['status'] != 'ok':
        from wi.utils.auth import logout
        error_code = response['status']
        error_msg = get_error(error_code)

        raise RestErrorException(error_msg)

    return response


def get_dict_from_list(list_of_dicts, key_value, key='id'):
    """
    Returns dictionary with key: @prm{key} equal to @prm{key_value} from a
    list of dictionaries: @prm{list_of_dicts}.
    """
    for dictionary in list_of_dicts:
        if dictionary.get(key) == None:
            raise Exception("No key: " + key + " in dictionary.")
        if dictionary.get(key) == key_value:
            return dictionary
    return None


def get_dicts_from_list(list_of_dicts, list_of_key_values, key='id'):
    """
    Returns list of dictionaries with keys: @prm{key} equal to one from list
    @prm{list_of_key_values} from a list of dictionaries: @prm{list_of_dicts}.
    """
    ret = []
    for dictionary in list_of_dicts:
        if dictionary.get(key) == None:
            raise Exception("No key: " + key + " in dictionary.")
        if dictionary.get(key) in list_of_key_values:
            ret.append(dictionary)
    return ret
