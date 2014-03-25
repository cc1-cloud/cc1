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

"""@package src.wi.recaptcha_django.middleware
"""


class ReCaptchaMiddleware(object):
    """
    A tiny middleware to automatically add IP address to ReCaptcha POST requests.
    """
    def process_request(self, request):
        """
        Adds recaptcha keys to POST.
        """
        if request.method == 'POST' and \
            'recaptcha_challenge_field' in request.POST and \
           'recaptcha_ip_field' not in request.POST:
            data = request.POST.copy()
            data['recaptcha_ip_field'] = request.META['REMOTE_ADDR']
            request.POST = data
