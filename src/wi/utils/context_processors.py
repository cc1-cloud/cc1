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

"""@package src.wi.utils.context_processors

@author Piotr Wójcik
@date 24.10.2011
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from common.states import cluster_states
from wi.utils.exceptions import RestErrorException
from wi.utils.views import prep_data


def add_variables(request):
    """
    Context processor for attaching CM list and other data to every request.
    """
    if request.session.get('user') == None:
        return {}

    try:
        rest_data = prep_data('guest/cluster/list_names/', request.session)
    except RestErrorException as ex:
        messages.error(request, ex.value)
        wi_logger = logging.getLogger('wi_logger')
        wi_logger.error('%s' % ex.value)
        return {}

    cm_list = rest_data

    none_available = True
    for item in cm_list:
        if item['state'] == cluster_states['ok']:
            none_available = False
            break

    if none_available:
        messages.error(request, _('No CM available.'))

    admin_cm_name = None
    for item in cm_list:
        if request.session['user'].is_admin_cm and request.session['user'].admin_cm_id == item['cluster_id']:
            admin_cm_name = item['name']

    return {'cm_list':        cm_list,
            'cluster_states': cluster_states,
            'admin_cm_name':  admin_cm_name,
            'VERSION':        settings.VERSION}
