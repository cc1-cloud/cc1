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

################################################################################
# Warning! Use dpkg-reconfigure <package> instead editing file settings.py!    #
# This will be overwritten by dpkg-reconfigure or system upgrade. If you need, #
# use settings.template.py and then reconfigure your package                   #
################################################################################

################################################################################
#    robimy ladna dokumentacje sphinksowa, czy ladnie wygladajaca w pliku?     #
################################################################################

# logging
import logging

# Logging directory. Inside CM will create directory per user for user's logs.
LOG_DIR = '/var/log/cc1/vmm/'

# Log level - WARNING, DEBUG, INFO or ERROR
LOG_LEVEL = logging.ERROR

# Log format for each entry
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

CA_BUNDLE = 'ca_bundle.crt'
CA_DIR = 'certs'
CTX_ADDRESS = 'https://ctx:8002'
