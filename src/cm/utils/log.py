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

"""@package src.cm.utils.log
"""

import logging
import os
from django.conf import settings

active_loggers = set([])


def get_logger(logger_id):
    if logger_id:
        log_name = 'user_%s' % str(logger_id)
    else:
        log_name = 'no_user'
        logger_id = 0
    if logger_id in active_loggers:
        return logging.getLogger(log_name)

    active_loggers.add(logger_id)
    logger = logging.getLogger(log_name)
    hdlr = logging.FileHandler(os.path.join(settings.LOG_DIR, '%s.log' % log_name))
    formatter = logging.Formatter(settings.LOG_FORMAT)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(settings.LOG_LEVEL)
    return logger


def debug(logger_id, text):
    get_logger(logger_id).debug(text)


def info(logger_id, text):
    get_logger(logger_id).info(text)


def warning(logger_id, text):
    get_logger(logger_id).warning(text)


def exception(logger_id, text):
    get_logger(logger_id).exception(text)


def error(logger_id, text):
    get_logger(logger_id).error(text)


active_ctx_loggers = set([])


def get_ctx_logger(logger_id):
    if logger_id:
        log_name = 'ip_%s' % str(logger_id)
    else:
        log_name = 'no_ip'
        logger_id = 0
    if logger_id in active_ctx_loggers:
        return logging.getLogger(log_name)

    active_ctx_loggers.add(logger_id)
    logger = logging.getLogger(log_name)
    hdlr = logging.FileHandler(os.path.join(settings.LOG_DIR, '%s.log' % log_name))
    formatter = logging.Formatter(settings.LOG_FORMAT)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(settings.LOG_LEVEL)
    return logger


def ctx_debug(logger_id, text):
    get_ctx_logger(logger_id).debug(text)


def ctx_info(logger_id, text):
    get_ctx_logger(logger_id).info(text)


def ctx_warning(logger_id, text):
    get_ctx_logger(logger_id).warning(text)


def ctx_exception(logger_id, text):
    get_ctx_logger(logger_id).exception(text)


def ctx_error(logger_id, text):
    get_ctx_logger(logger_id).error(text)


active_thread_loggers = set([])


def get_thread_logger(logger_id):
    if logger_id:
        log_name = 'thread_%d' % logger_id
    else:
        log_name = 'no_thread'
        logger_id = 0
    if logger_id in active_thread_loggers:
        return logging.getLogger(log_name)

    active_thread_loggers.add(logger_id)
    logger = logging.getLogger(log_name)
    hdlr = logging.FileHandler(os.path.join(settings.LOG_DIR, '%s.log' % log_name))
    formatter = logging.Formatter(settings.LOG_FORMAT)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(settings.LOG_LEVEL)
    return logger


def thread_debug(logger_id, text):
    get_thread_logger(logger_id).debug(text)


def thread_info(logger_id, text):
    get_thread_logger(logger_id).info(text)


def thread_warning(logger_id, text):
    get_thread_logger(logger_id).warning(text)


def thread_exception(logger_id, text):
    get_thread_logger(logger_id).exception(text)


def thread_error(logger_id, text):
    get_thread_logger(logger_id).error(text)
