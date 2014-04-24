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

"""@package src.wi.urls.admin_cm.farm

@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ungettext, ugettext_lazy as _

from wi.forms.vm import EditVMForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import generic_multiple_id, form_generic_id


farm_patterns = patterns('wi.views.admin_cm.farm',
    url(r'^farms/$', 'cma_farms', name='cma_farms'),
    url(r'^ajax/cm/farms_get_table/(?P<user_id>\d+)/$', 'cma_farms_ajax_get_table', name='cma_farms_ajax_get_table'),
    url(r'^ajax/cm/farm_details/(?P<id1>\d+)/$', 'cma_farms_ajax_details', name='cma_farms_ajax_details'),
    url(r'^ajax/cm/farm_destroy/$', admin_cm_permission(generic_multiple_id),
        {'template_name':       'generic/simple.html',
         'success_msg':         (lambda desc, count: ungettext('You have successfully destroyed farm <b>%(desc)s</b>.', 'You have successfully destroyed %(count)d farms (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Do you want to destroy farm <b>%(desc)s</b>?', 'Do you want to destroy %(count)d farms <b>%(desc)s</b>?', count) % {'desc': desc, 'count': count}),
         'request_url':         'admin_cm/farm/destroy/',
         'id_key':              'farm_ids', },
        name='cma_farms_ajax_destroy'),
    url(r'^ajax/cm/farm_erase/$', admin_cm_permission(generic_multiple_id),
        {'template_name':       'generic/simple.html',
         'success_msg':         (lambda desc, count: ungettext('You have successfully erased farm <b>%(desc)s</b>.', 'You have successfully erased %(count)d farms (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Do you want to erase farm <b>%(desc)s</b>?', 'Do you want to erase %(count)d farms <b>%(desc)s</b>?', count) % {'desc': desc, 'count': count}),
         'request_url':         'admin_cm/farm/erase/',
         'id_key':              'farm_ids', },
        name='cma_farms_ajax_erase'),
    url(r'^ajax/cm/save_and_shutdown_farm/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('Farm head will be saved.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('The farm will be closed. Enter a name to save head of this farm.') % {'desc': desc}),
         'confirmation':         _('Save and shutdown'),
         'request_url_post':    'admin_cm/farm/save_and_shutdown/',
         'request_url_get':     'admin_cm/farm/get_by_id/',
         'id_key':              'farm_id',
         'form_class':           EditVMForm},
        name='cma_farms_ajax_save_and_shutdown'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(farm_patterns)),
)
