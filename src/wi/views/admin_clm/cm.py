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

"""@package src.wi.views.admin_clm.cm
@author Piotr Wójcik
@author Krzysztof Danielowski
@date 21.09.2010
"""

from wi.utils import messages_ajax
from wi.utils.decorators import admin_clm_permission, django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import cm_active_reversed as cm_states
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_clm_permission
def clm_ajax_get_table_cms(request):
    """
    Ajax view for fetching Cluster Manager list.
    """
    if request.method == 'GET':
        cms = prep_data('admin_clm/cluster/get_list/', request.session)

        for item in cms:
            item['is_activeName'] = unicode(cm_states[item['state']])

        return messages_ajax.success(cms)
