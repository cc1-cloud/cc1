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

"""@package src.wi.views.admin_cm.template
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.02.2012
"""

from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.utils import messages_ajax
from wi.utils.decorators import admin_cm_permission
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import ec2names_reversed
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_table_templates(request):
    """
    Ajax view fetching template list.
    """
    if request.method == 'GET':
        templates = prep_data('admin_cm/template/get_list/', request.session)

        for item in templates:
            item['ec2name'] = ec2names_reversed[item['ec2name']]
            item['memory'] = filesizeformatmb(item['memory'])

        return messages_ajax.success(templates)
