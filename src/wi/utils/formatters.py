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

"""@package src.wi.utils.formatters

@author Piotr Wójcik
@date 24.03.2011
"""

from django.utils.translation import ngettext, ugettext_lazy as _
from django.utils.encoding import force_unicode


def time_from_sec(seconds, separator=', '):
    """
    Takes an amount of seconds and turns it into a human-readable amount of time.
    """

    suffixes = [(lambda count: ngettext(' day', ' days', count) % {'count': count}),
                (lambda count: _(' h') % {'count': count}),
                (lambda count: _(' min') % {'count': count}),
                (lambda count: _(' s') % {'count': count})]

    # the formatted time string to be returned
    time = []

    # the pieces of time to iterate over (days, hours, minutes, etc)
    # - the first piece in each tuple is the suffix (d, h, w)
    # - the second piece is the length in seconds (a day is 60s * 60m * 24h)
    parts = [(suffixes[0], 60 * 60 * 24),
             (suffixes[1], 60 * 60),
             (suffixes[2], 60),
             (suffixes[3], 1)]

    # for each time piece, grab the value and remaining seconds, and add it to
    # the time string
    for suffix, length in parts:
        value = seconds / length
        if value > 0:
            seconds = seconds % length
            time.append('%s%s' % (str(value), force_unicode(suffix(int(value)))))  # (suffix, (suffix, suffix + 's')[value > 1])[add_s]))
        if seconds < 1:
            break

    return separator.join(time)
