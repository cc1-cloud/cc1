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

"""@package src.wi.urls.admin_cm.vm
@author Krzysztof Danielowski, Piotr Wojcik
@date 17.03.2011
"""

from django.conf.urls import url, patterns, include
from django.utils.translation import ungettext, ugettext_lazy as _

from wi.forms.vm import EditVMForm
from wi.utils.decorators import admin_cm_permission
from wi.utils.views import generic_multiple_id, simple_generic_id, \
    form_generic_id

vm_patterns = patterns('wi.views.admin_cm.vm',
    url(r'^vms/$', 'cma_vms', name='cma_vms'),
    url(r'^ajax/cm/vms_get_table/(?P<user_id>\d+)/$', 'cma_vms_ajax_get_table', name='cma_vms_ajax_get_table'),
    url(r'^ajax/cm/vm_details/(?P<vm_id>\d+)/$', 'cma_vms_ajax_vm_details', name='cma_vms_ajax_vm_details'),
    url(r'^ajax/cm/vm_destroy/$', admin_cm_permission(generic_multiple_id),
        {'template_name':       'generic/simple.html',
         'success_msg':         (lambda desc, count: ungettext('You have successfully destroyed virtual machine <b>%(desc)s</b>.', 'You have successfully destroyed %(count)d virtual machines (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Do you want to destroy virtual machine <b>%(desc)s</b>?', 'Do you want to destroy %(count)d virtual machines <b>%(desc)s</b>?', count) % {'desc': desc, 'count': count}),
         'request_url':         'admin_cm/vm/destroy/',
         'id_key':              'vm_id_list'
         },
        name='cma_vms_ajax_destroy'),
    url(r'^ajax/cm/vm_erase/$', admin_cm_permission(generic_multiple_id),
        {'template_name':       'generic/simple.html',
         'success_msg':         (lambda desc, count: ungettext('You have successfully erased virtual machine <b>%(desc)s</b>.', 'You have successfully erased %(count)d virtuals machines (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Do you want to erase virtual machine <b>%(desc)s</b>?', 'Do you want to erase %(count)d virtual machines <b>%(desc)s</b>?', count) % {'desc': desc, 'count': count}),
         'request_url':         'admin_cm/vm/erase/',
         'id_key':              'vm_id_list'
         },
        name='cma_vms_ajax_erase'),
    url(r'^ajax/cm/revoke_ip/(?P<id1>\d+)/$', admin_cm_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully revoked IP address.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to revoke IP address?') % {'desc': desc}),
         'request_url':     'admin_cm/public_ip/unassign/',
         'id_key':          'lease_id', },
        name='cma_vms_ajax_revoke_ip'),
    url(r'^ajax/cm/vm_save_and_shutdown/(?P<id1>\d+)/$', admin_cm_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('Virtual machine will be saved.') % {'desc': desc}),
         'confirmation':         _('Save and shutdown'),
         'request_url_post':     'admin_cm/vm/save_and_shutdown/',
         'request_url_get':      'admin_cm/vm/get_by_id/',
         'id_key':               'vm_id',
         'form_class':           EditVMForm},
        name='cma_vms_ajax_save_and_shutdown'),
)

urlpatterns = patterns('',
    url(r'^admin_cm/', include(vm_patterns)),
)
