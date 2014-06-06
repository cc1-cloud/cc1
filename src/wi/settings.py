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

"""@package src.wi.settings

@author Piotr Wójcik
@author Krzysztof Danielowski
@date 21.09.2010
"""

try:
    from config import CLOUD_MANAGER_ADDRESS, LOG_LEVEL, LOG_DIR, WI_DATA, SECRET_KEY
except Exception, ex:
    print "Error importing WI configuration file: config.py\nReason: %s" % str(ex)
    exit()

import os
import logging

ALLOWED_HOSTS = ['*']

VERSION = '2.0'

PROJECT_DIR = os.path.dirname(__file__)

#############################################
# WI specific settings for cc1 project.     #
#############################################
CAPTCHA = True

# priv/pub keys to reCaptcha bound to common account cc1.ifj@gmail.com
RECAPTCHA_PUBLIC_KEY = '6LenDtcSAAAAAJLrj1MBBAVGIaOjo3PNFZc7FDc4'
RECAPTCHA_PRIVATE_KEY = '6LenDtcSAAAAAKisRsijUTTOEWAtr6yBNg1Cl_AL'

# port on which NoVNC proxy is running
NOVNC_PORT = 6080

import json

# logging
LOG_FORMAT = "%(asctime)s %(levelname)s - %(message)s"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'wi_logger': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'wi.log').replace('\\', '/'),
            'formatter': 'verbose'
        },
        'request': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'request.log').replace('\\', '/'),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'wi_logger': {
            'handlers': ['console', 'wi_logger'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'request': {
            'handlers': ['console', 'request'],
            'propagate': False,
            'level': 'DEBUG',
        }
    }
}

# js states file
from common.states import vm_states, farm_states, image_states, node_states, user_active_states as user_states

JS_STATES_FILE = os.path.join(PROJECT_DIR, 'media/js/states.js').replace('\\', '/')
file_js_states = open(JS_STATES_FILE, 'w')
file_js_states.write(''.join(('cc1.states.vm = ', json.dumps(vm_states), ';')))
file_js_states.write(''.join(('cc1.states.farm = ', json.dumps(farm_states), ';')))
file_js_states.write(''.join(('cc1.states.image = ', json.dumps(image_states), ';')))
file_js_states.write(''.join(('cc1.states.user = ', json.dumps(user_states), ';')))
file_js_states.write(''.join(('cc1.states.node = ', json.dumps(node_states), ';')))
file_js_states.close()


#############################################
# Django specific settings for cc1 project. #
#############################################
DEBUG = False
TEMPLATE_DEBUG = DEBUG

WSGI_APPLICATION = 'wi.wsgi.application'

ROOT_URLCONF = 'wi.urls'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

## Local time zone for this installation. Choices can be found here:
#  http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
#  although not all choices may be available on all operating systems.
#  On Unix systems, a value of None will cause Django to use the same
#  timezone as the operating system.
#  If running in a Windows environment this must be set to the same as your
#  system time zone.
TIME_ZONE = 'Europe/Warsaw'

LANGUAGE_CODE = 'pl'

ugettext = lambda s: s

LANGUAGES = (
    ('pl', ugettext('Polski')),
    ('en', ugettext('English')),
)

SITE_ID = 1

TEMPLATE_STRING_IF_INVALID = 'empty'

## If you set this to False, Django will make some optimizations so as not
#  to load the internationalization machinery.
USE_I18N = True

## If you set this to False, Django will not format dates, numbers and
#  calendars according to the current locale
USE_L10N = True

## Absolute path to the directory that holds media.
#  Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

## URL that handles the media served from MEDIA_ROOT. Make sure to use a
#  trailing slash if there is a path component (optional in other cases).
#  Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

## URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
#  trailing slash.
#  Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

## List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'wi.utils.context_processors.add_variables',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'wi.recaptcha_django.middleware.ReCaptchaMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale').replace('\\', '/'),
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates').replace('\\', '/'),
)

INSTALLED_APPS = (
    'wi.commontags',
    'wi.recaptcha_django',
    'wi.utils',
)

## Session settings
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/auth/login/'
LOGOUT_URL = '/auth/logout/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
