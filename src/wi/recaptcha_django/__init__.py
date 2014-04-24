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

"""@package src.wi.recaptcha_django

\c ReCAPTCHA (Completely Automated Public Turing test to tell Computers and
Humans Apart - while helping digitize books, newspapers, and old time radio
shows) module for django
"""

from django.conf import settings
from django.forms import Widget, Field, ValidationError
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext_lazy as _
from recaptcha.client import captcha


HUMAN_ERRORS = {
    'unknown':                  _(u'Unknown error.'),
    'invalid-site-public-key':  _(u'ReCAPTCHA is wrongly configured.'),
    'invalid-site-private-key': _(u'ReCAPTCHA is wrongly configured.'),
    'invalid-request-cookie':   _(u'Bad reCAPTCHA challenge parameter.'),
    'incorrect-captcha-sol':    _(u'The CAPTCHA solution was incorrect.'),
    'verify-params-incorrect':  _(u'Bad reCAPTCHA verification parameters.'),
    'invalid-referrer':         _(u'Provided reCAPTCHA API keys are not valid for this domain.'),
    'recaptcha-not-reachable':  _(u'ReCAPTCHA could not be reached.')
}


class ReCaptchaWidget(Widget):
    """
    A Widget that renders a \c ReCAPTCHA form.
    """

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        error = final_attrs.get('error', None)
        html = captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY, error=error, use_ssl=True)

        return mark_safe(u"""<script type="text/javascript">
        var RecaptchaOptions = {
            custom_translations : {
                instructions_visual : "%s",
                instructions_audio : "%s",
                play_again : "%s",
                cant_hear_this : "%s",
                visual_challenge : "%s",
                audio_challenge : "%s",
                refresh_btn : "%s",
                help_btn : "%s",
                incorrect_try_again : "%s",
            },
            theme : 'clean'
        };
        </script>
        %s
        """ % (_('Type the two words:'),
               _('Type what you hear:'),
               _('Play sound again'),
               _('Download sound as MP3'),
               _('Get a visual challenge'),
               _('Get an audio challenge'),
               _('Get a new challenge'),
               _('Help'),
               _('Incorrect. Try again.'),
                html))

    def value_from_datadict(self, data, files, name):
        """
        Generates Widget value from \c data dictionary.
        """
        try:
            return {'challenge': data['recaptcha_challenge_field'],
                    'response': data['recaptcha_response_field'],
                    'ip': data['recaptcha_ip_field']}
        except KeyError:
            return None


class ReCaptchaField(Field):
    """
    Field definition for a \c ReCAPTCHA.
    """
    widget = ReCaptchaWidget

    def clean(self, value):
        if value is None:
            raise ValidationError(_('Invalid request'))
        resp = captcha.submit(value.get('challenge', None),
                              value.get('response', None),
                              settings.RECAPTCHA_PRIVATE_KEY,
                              value.get('ip', None))
        if not resp.is_valid:
            self.widget.attrs['error'] = resp.error_code
            raise ValidationError(HUMAN_ERRORS.get(resp.error_code, _(u'Unknown error.')))
