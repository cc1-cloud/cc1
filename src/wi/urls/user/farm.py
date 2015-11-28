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

"""@package src.wi.urls.user.farm

@author Piotr Wójcik
@date 14.11.2011
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ugettext_lazy as _

from wi.forms.farm import CreateFarmForm1, CreateFarmForm2, CreateFarmForm3, CreateFarmForm4
from wi.forms.vm import EditVMForm
from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, simple_generic_id, form_generic_id
from wi.views.user.farm import CreateFarmWizard


farm_patterns = patterns('wi.views.user.farm',
    url(r'^$', user_permission(direct_to_template), {'template_name': 'farms/base.html'}, name='far_farms'),

    url(r'^potato/$', user_permission(direct_to_template), {'template_name': 'farms/potato.html'}, name='far_potato'),

    url(r'^create_farm/$', CreateFarmWizard.as_view([CreateFarmForm1, CreateFarmForm2, CreateFarmForm3, CreateFarmForm4]),
        name='far_create_farm'),
    url(r'^show_farm/$', user_permission(direct_to_template), {'template_name': 'farms/show_farm.html'}, name='far_show_farm'),

    url(r'^ajax/get_table/$', 'far_ajax_get_table', name='far_ajax_get_table'),
    url(r'^ajax/destroy_farm/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully destroyed farm <b>%(desc)s</b>.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you really want to destroy farm <b>%(desc)s</b>?') % {'desc': desc}),
         'request_url':     'user/farm/destroy/',
         'id_key':          'farm_id',
         },
        name='far_ajax_destroy_farm'),
    url(r'^ajax/save_and_shutdown_farm/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('Farm head will be saved.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('The farm will be closed. Enter a name to save head of this farm.') % {'desc': desc}),
         'confirmation':         _('Save and shutdown'),
         'request_url_post':     'user/farm/save_and_shutdown/',
         'request_url_get':      'user/farm/get_by_id/',
         'form_class':           EditVMForm,
         'id_key':              'farm_id', },
        name='far_ajax_save_and_shutdown'),
)


urlpatterns = patterns('',
    url(r'^farm/', include(farm_patterns)),
)
