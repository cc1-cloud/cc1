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

"""@package src.wi.urls.user.vm

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 26.11.2010
"""

from django.conf.urls import patterns, url, include
from django.utils.translation import ungettext, ugettext_lazy as _

from wi.utils.decorators import user_permission
from wi.utils.views import direct_to_template, simple_generic_id, \
    form_generic_id, generic_multiple_id, generic_multiple_id_form
from wi.views.user.vm import CreateVMWizard
from wi.forms.vm import ChangeVMPasswordForm, EditVMForm, SetSshKeyForm, \
    AssignChosenIPForm, CreateVMForm1, CreateVMForm2, CreateVMForm3, CreateVMForm4, \
    MonitoringVMForm


vm_patterns = patterns('wi.views.user.vm',
    url(r'^$', user_permission(direct_to_template), {'template_name': 'vms/base.html'}, name='vms_vms'),

    url(r'^create_vm/$', CreateVMWizard.as_view([CreateVMForm1, CreateVMForm2, CreateVMForm3, CreateVMForm4]), name='vms_create_vm'),
    url(r'^show_vm/$', user_permission(direct_to_template), {'template_name': 'vms/show_vm.html'}, name='vms_show_vm'),

    url(r'^vnc/(?P<vm_id>\d+)/$', 'vms_vnc', name='vms_vnc'),
    url(r'^ajax/vnc_configured/$', 'vms_ajax_vnc_configured', name='vms_ajax_vnc_configured'),

    url(r'^ajax/vm_details/(?P<vm_id>\d+)/$', 'vms_ajax_vm_details', name='vms_ajax_vm_details'),
    url(r'^ajax/get_table/$', 'vms_ajax_get_table', name='vms_ajax_get_table'),

    url(r'^ajax/ssh_key/$', user_permission(generic_multiple_id_form),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, count: ungettext('SSH key has been copied successfully to <b>%(desc)s</b>.', 'SSH key has been copied successfully to %(count)d virtual machines (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Enter a public key to set for machine <b>%(desc)s</b>.', 'Enter a public key to set for %(count)d machines <b>%(desc)s</b>.', count) % {'desc': desc, 'count': count}),
         'confirmation':        _('Set key'),
         'request_url':         'user/ctx/add_ssh_key/',
         'form_class':          SetSshKeyForm,
         'request_url_both':    {'keys': 'user/key/get_list/'},
         'id_key':              'vm_ids'
         },
        name='vms_ajax_ssh_key'),
    url(r'^ajax/reset_password/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('Password has been set to: (<b>%(password)s</b>) on machine: <b>%(desc)s</b>.') % {'password': data['password'], 'desc': desc}),
         'ask_msg':              (lambda desc: _('Reset machine <b>%(desc)s</b> password for selected user.') % {'desc': desc}),
         'confirmation':         _('Reset password'),
         'request_url_post':    'user/ctx/reset_password/',
         'form_class':           ChangeVMPasswordForm,
         'ajax_success_status':  7999,  # for 'info' class of the popup
         'id_key':              'vm_id'
         },
        name='vms_ajax_reset_password'),
    url(r'^ajax/destroy/$', user_permission(generic_multiple_id),
        {'template_name':       'generic/simple.html',
         'success_msg':         (lambda desc, count: ungettext('You have successfully destroyed virtual machine <b>%(desc)s</b>.', 'You have successfully destroyed %(count)d virtual machines (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Do you want to destroy virtual machine <b>%(desc)s</b>?<br /><b>Note!</b> If you would like to use this machine later make sure to use the <b>Save and shutdown</b> option instead!<br /> We recommend to manually unmount any attached storage disks.',
                                                               'Do you want to destroy %(count)d virtual machines <b>%(desc)s</b>?<br /><b>Note!</b> If you would like to use this machine later make sure to use the <b>Save and shutdown</b> option instead!<br /> We recommend to manually unmount any attached storage disks.', count) % {'desc': desc, 'count': count}),
         'request_url':         'user/vm/destroy/',
         'id_key':              'vm_ids'
         },
        name='vms_ajax_destroy'),
    url(r'^ajax/restart/$', user_permission(generic_multiple_id),
        {'template_name':       'generic/simple.html',
         'success_msg':         (lambda desc, count: ungettext('You have successfully rebooted virtual machine <b>%(desc)s</b>.', 'You have successfully rebooted %(count)d virtual machines (<b>%(desc)s</b>).', count) % {'desc': desc, 'count': count}),
         'ask_msg':             (lambda desc, count: ungettext('Do you want to reset virtual machine <b>%(desc)s</b>?.<br /><b>Note!</b> Any unsaved data will be lost!', 'Do you want to reset %(count)d virtual machines <b>%(desc)s</b>?.<br /><b>Note!</b> Any unsaved data will be lost!', count) % {'desc': desc, 'count': count}),
         'request_url':         'user/vm/reset/',
         'id_key':              'vm_ids'
        },
        name='vms_ajax_restart'),

    url(r'^ajax/assign_chosen_ip/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':       'vms/ajax/assign_ip.html',
         'success_msg':         (lambda desc, data: _('You have successfully assigned selected IP address.') % {'desc': desc}),
         'ask_msg':             (lambda desc: _('Select an IP address to assign:') % {'desc': desc}),
         'confirmation':        _('Assign selected IP'),
         'request_url_post':    'user/public_ip/assign/',
         'form_class':          AssignChosenIPForm,
         'request_url_both':    {'ips': 'user/public_ip/get_list/'},
         'id_key':              'lease_id'
         },
        name='vms_ajax_assign_chosen_ip'),

    url(r'^ajax/assign_ip/(?P<vm_id>\d+)/$', 'vms_ajax_assign_ip', name='vms_ajax_assign_ip'),

    url(r'^ajax/revoke_chosen_ip/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully revoked IP address.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to revoke IP address?') % {'desc': desc}),
         'request_url':     'user/public_ip/unassign/',
         'id_key':          'lease_id'
         },
        name='vms_ajax_revoke_chosen_ip'),

    url(r'^ajax/revoke_ip/(?P<vm_id>\d+)/$', 'vms_ajax_revoke_ip', name='vms_ajax_revoke_ip'),
    url(r'^ajax/assign_disk/(?P<vm_id>\d+)/$', 'vms_ajax_assign_disk', name='vms_ajax_assign_disk'),
    url(r'^ajax/revoke_disk/(?P<vm_id>\d+)/$', 'vms_ajax_revoke_disk', name='vms_ajax_revoke_disk'),

    url(r'^ajax/edit_vm/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':       'generic/form.html',
         'success_msg':         (lambda desc, data: _('You have successfully edited virtual machine data.') % {'desc': desc}),
         'confirmation':        _('Save'),
         'request_url_post':    'user/vm/edit/',
         'request_url_get':     'user/vm/get_by_id/',
         'form_class':          EditVMForm,
         'id_key':              'vm_id'},
        name='vms_ajax_edit_vm'),

    url(r'^ajax/save_and_shutdown/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':        'generic/form.html',
         'success_msg':          (lambda desc, data: _('Virtual machine will be saved.') % {'desc': desc}),
         'ask_msg':              (lambda desc: _('Enter a name to save virtual machine <b>%(desc)s</b>:') % {'desc': desc}),
         'confirmation':         _('Save and shutdown'),
         'request_url_post':    'user/vm/save_and_shutdown/',
         'request_url_get':     'user/vm/get_by_id/',
         'form_class':           EditVMForm,
         'id_key':              'vm_id'},
        name='vms_ajax_save_and_shutdown'),

    url(r'^ajax/set_vnc/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully enabled VNC.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to enable VNC?') % {'desc': desc}),
         'request_url':     'user/vm/attach_vnc/',
         'id_key':          'vm_id'
         },
        name='vms_ajax_set_vnc'),
    url(r'^ajax/unset_vnc/(?P<id1>\d+)/$', user_permission(simple_generic_id),
        {'template_name':   'generic/simple.html',
         'success_msg':     (lambda desc: _('You have successfully disabled VNC.') % {'desc': desc}),
         'ask_msg':         (lambda desc: _('Do you want to disable VNC?') % {'desc': desc}),
         'request_url':     'user/vm/detach_vnc/',
         'id_key':          'vm_id'
        },
        name='vms_ajax_unset_vnc'),

    url(r'^ajax/get_template_list/$', 'vms_ajax_get_template_list', name='vms_ajax_get_template_list'),

    url(r'^ajax/monitoring/(?P<id1>\d+)/$', user_permission(form_generic_id),
        {'template_name':           'vms/ajax/monitoring.html',
         'form_class':              MonitoringVMForm,
         'success_msg':             (lambda desc, data: data),
         'request_url_post':        'user/monia/vm_stats/',
         'id_key':                  'vm_id'
        },
        name='vms_ajax_vm_monitoring'),
)


urlpatterns = patterns('',
    url(r'^vm/', include(vm_patterns)),
)
