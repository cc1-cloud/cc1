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

"""@package src.wi.utils.regexp

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 1.07.2011

Module contains dictionaries: \c regexp and \c regext_text. Both dictionaries contain fields corresponding to user infos.

    - \c regexp: Each field contains regular expressions consisging of the characters avaliable in strings describing that user info.

    - \c regexp_text: Each field contains message (in human-readable form) about how user info should be filled.
"""

import re

from django.utils.translation import ugettext as _


regexp = {'login':      re.compile(r'^[a-zA-Z0-9_]+$'),
          'password':   re.compile(r'^[ -~]+$'),
          'dev_name':   re.compile(r'^[0-9a-z]([0-9a-z\-]{0,38}[0-9a-z])?$')
}

regexp_text = {'login':     _('This value must contain only letters, numbers and underscores.'),
               'password':  _('This value must not contain any diacritic marks.'),
               'dev_name':  _('This value must contain only small letters, numbers and dashes.'),
}
