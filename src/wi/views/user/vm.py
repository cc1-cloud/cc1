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

"""@package src.wi.views.user.vm
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 26.11.2010
"""

from colorsys import hsv_to_rgb
import os

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from common.states import vm_states
from wi.utils.decorators import user_permission
from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.utils import messages_ajax, parsing
import wi.utils as utils
from wi.utils.decorators import django_view
from wi.utils.exceptions import RestErrorException
from wi.utils.formatters import time_from_sec
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import vm_states_reversed, ec2names_reversed
from wi.utils.views import prep_data, CustomWizardView
from wi.forms.vm import AssignIPForm, RevokeIPForm, RevokeDiskForm, \
    AssignDiskForm


class CreateVMWizard(CustomWizardView):
    """
    Wizard handling virtual machine creation views.
    """
    url_done = 'vms_show_vm'
    url_start = 'vms_create_vm'

    wizard_name = 'create_vm_wizard'
    template_dir_name = 'vms'

    def done(self, form_list, **kwargs):
        form_data = self.get_all_cleaned_data()
        try:
            prep_data(('user/vm/create/', form_data), self.request.session)
        except RestErrorException as ex:
            messages.error(self.request, ex.value)
        else:
            messages.success(self.request, _('Virtual machine is being created.'))

        return redirect(self.url_done)

    def get_form_kwargs(self, step=None):
        step = int(step)
        initial_data = {}

        if step == 2:
            rest_data = prep_data({'ips': 'user/public_ip/get_list/',
                                   'disks': 'user/storage_image/get_list/',
                                   'iso': 'user/iso_image/get_list/',
                                  }, self.request.session)

            initial_data = {'rest_data': rest_data}

        return initial_data

    def get_context_data(self, form, **kwargs):
        context = super(CreateVMWizard, self).get_context_data(form=form, **kwargs)

        context.update({'steps_desc': [_('Image'), _('Hardware'), _('Optional resources'), _('Summary')]})

        if self.steps.current == '0':
            rest_data = prep_data({'groups': 'user/group/list_groups/'}, self.request.session)
            categories = [
                          ['all', _('All images')],
                          ['private', _('My images')],
                          ['public', _('Public images')],
                         ]
            for item in parsing.parse_groups(rest_data):
                categories.append([item[0], _('Group images: ') + item[1]])

            context.update({'image_categories': categories})

        elif self.steps.current == '3':
            form_cleaned_data = self.get_all_cleaned_data()
            rest_data = prep_data({'image': ('user/system_image/get_by_id/', {'system_image_id': form_cleaned_data['image_id']}),
                                   'templates': 'user/template/get_list/',
                                   'ips': 'user/public_ip/get_list/',
                                   'disks': 'user/storage_image/get_list/',
                                   'iso': 'user/iso_image/get_list/',
                                   }, self.request.session)

            summary_data = {'summary_image': rest_data['image'],
                            'summary_template': utils.get_dict_from_list(rest_data['templates'], form_cleaned_data['template_id'], key='template_id'),
                            'summary_ip': utils.get_dict_from_list(rest_data['ips'], form_cleaned_data['public_ip_id'], key='public_ip_id'),
                            'summary_disks': utils.get_dicts_from_list(rest_data['disks'], form_cleaned_data['disk_list'], key='storage_image_id'),
                            'summary_iso': utils.get_dicts_from_list(rest_data['iso'], form_cleaned_data['iso_list'], key='iso_image_id'),
                            'summary_vnc': form_cleaned_data['vnc'],
                            }

            context.update(summary_data)

        return context

CreateVMWizard.dispatch = method_decorator(user_permission)(
                            method_decorator(django_view)(
                                CreateVMWizard.dispatch))


@django_view
@ajax_request
@user_permission
def vms_ajax_get_table(request):
    """
    Ajax view for fetching virtual machines list.
    """
    if request.method == 'GET':
        rest_data = prep_data('user/vm/get_list/', request.session)

        for item in rest_data:
            item['stateName'] = vm_states_reversed[item['state']]
            item['cpuLoadPercent'] = int(min(float(item['cpu_load'].get('60') or 0) * 100, 100))
            item['cpuLoadColor'] = "#%02x%02x%02x" % tuple(i * 255 for i in hsv_to_rgb(float(item['cpuLoadPercent']) / 300, 1.0, 0.8))
            item['pub_ip'] = []
            for i in item['leases']:
                if i['public_ip'] != "":
                    item['pub_ip'].append(i['public_ip']['address'])
            item['stringIP'] = ', '.join(item['pub_ip'])
            item['stringISO'] = ', '.join([iso['name'] for iso in item['iso_images']])
            item['stringDisk'] = ', '.join([disk['name'] for disk in item['storage_images']])

        return messages_ajax.success(rest_data)


@django_view
@ajax_request
@user_permission
def vms_ajax_vm_details(request, vm_id, template_name='vms/ajax/vm_details.html'):
    """
    Ajax view fetching virtual machine details.
    """
    if request.method == 'POST':
        vm = prep_data(('user/vm/get_by_id/', {'vm_id': vm_id}), request.session)

        if vm['state'] == vm_states['closed']:
            return messages_ajax.success('', status=1)

        vm['uptime'] = time_from_sec(vm['uptime'])

        return messages_ajax.success(
                    render_to_string(template_name,
                                    {'vm_id': vm_id,
                                     'item': vm,
                                     'states_reversed': vm_states_reversed,
                                     'states': vm_states},
                                     context_instance=RequestContext(request)))


@django_view
@user_permission
def vms_vnc(request, vm_id, template_name='vms/vnc.html'):
    """
    VNC applet view.
    """
    if request.POST is None or request.POST.get('vnc_endpoint') is None or request.POST.get('vnc_passwd') is None:
        vnc_host, vnc_port, vnc_pass = '', '', ''
    else:
        vnc_endpoint = request.POST['vnc_endpoint'].split(':')
        vnc_host, vnc_port, vnc_pass = vnc_endpoint[0], vnc_endpoint[1], request.POST['vnc_passwd']

    return render_to_response(template_name, {'vnc_viewer_jar': settings.VNC_VIEWER_JAR,
                                              'vnc_host': vnc_host,
                                              'vnc_port': vnc_port,
                                              'vnc_passwd': vnc_pass,
                                              'vmid': vm_id
                                             }, context_instance=RequestContext(request))


@django_view
@ajax_request
@user_permission
def vms_ajax_vnc_configured(request):
    """
    Ajax view checking if VNC applet is configured.
    """
    vnc_jar_file = os.path.join(settings.MEDIA_ROOT, 'applets/vnc', settings.VNC_VIEWER_JAR).replace('\\', '/')
    if os.path.isfile(vnc_jar_file):
        return messages_ajax.success('configured')

    return messages_ajax.error(_('VNC Viewer applet is not configured. Please contact system administrator. Meantime you may use a standalone VNC client.'))


@django_view
@ajax_request
@user_permission
def vms_ajax_get_template_list(request):
    """
    Ajax view fetching template list.
    """
    if request.method == 'GET':
        rest_data = prep_data('user/template/get_list/', request.session)

        for item in rest_data:
            item['memory'] = filesizeformatmb(item['memory'])
            if item['ec2name'] != 0:
                item['ec2fullname'] = ec2names_reversed[item['ec2name']]

        return messages_ajax.success(rest_data)


@django_view
@ajax_request
@user_permission
@csrf_protect
def vms_ajax_revoke_ip(request, vm_id, template_name='generic/form.html', form_class=RevokeIPForm):
    """
    Ajax view for detaching elastip IP from a virtual machine.
    """
    rest_data = prep_data({'vm': ('user/vm/get_by_id/', {'vm_id': vm_id})}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            prep_data(('user/public_ip/unassign/', {'public_ip_id': form.cleaned_data['public_ip_id']}), request.session)
            return messages_ajax.success(_('You have successfully revoked IP address.'))
    else:
        form = form_class(rest_data=rest_data)

    return messages_ajax.success(render_to_string(template_name,
                                                   {'form': form,
                                                    'text': _('Select an IP address to revoke:'),
                                                    'confirmation': _('Revoke')},
                                                   context_instance=RequestContext(request)),
                                  status=1)


@django_view
@ajax_request
@user_permission
@csrf_protect
def vms_ajax_assign_ip(request, vm_id, template_name='vms/ajax/assign_ip.html', form_class=AssignIPForm):
    """
    Ajax view for attaching IP address to a virtual machine.
    """
    rest_data = prep_data({'ips': 'user/public_ip/get_list/',
                           'vm': ('user/vm/get_by_id/', {'vm_id': vm_id})}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            prep_data(('user/public_ip/assign/', form.cleaned_data), request.session)
            return messages_ajax.success(_('You have successfully assigned selected IP address.'))
    else:
        form = form_class(rest_data=rest_data)

    return messages_ajax.success(render_to_string(template_name,
                                                  {'form': form,
                                                   'text': _('Select an IP address and lease to assign:'),
                                                   'confirmation': _('Assign')},
                                                   context_instance=RequestContext(request)),
                                  status=1)


@django_view
@ajax_request
@user_permission
@csrf_protect
def vms_ajax_revoke_disk(request, vm_id, template_name='vms/ajax/revoke_disk.html', form_class=RevokeDiskForm):
    """
    Ajax view for detaching a disk from a virtual machine.
    """
    rest_data = prep_data({'vm': ('user/vm/get_by_id/', {'vm_id': vm_id}),
                           'disk_controllers': 'user/storage_image/get_disk_controllers/'}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            form.cleaned_data['vm_id'] = int(vm_id)
            prep_data(('user/storage_image/detach/', form.cleaned_data), request.session)

            return messages_ajax.success(_('Disk has been revoked.'))
    else:
        form = form_class(rest_data=rest_data)

    return messages_ajax.success(render_to_string(template_name,
                                                   {'form': form,
                                                    'text': '',
                                                    'confirmation': _('Revoke disk')},
                                                   context_instance=RequestContext(request)),
                                  status=1)


@django_view
@ajax_request
@user_permission
@csrf_protect
def vms_ajax_assign_disk(request, vm_id, template_name='vms/ajax/assign_disk.html', form_class=AssignDiskForm):
    """
    Ajax view for assigning Disk to a virtual machine.
    """
    rest_data = prep_data({'disks': 'user/storage_image/get_list/',
                           'disk_controllers': 'user/storage_image/get_disk_controllers/'
                          }, request.session)

    live_attach = []
    for item in rest_data['disk_controllers']:
        if item['live_attach'] == True:
            live_attach.append(item['id'])

    disks_list = []
    for item in rest_data['disks']:
        if item['disk_controller'] in live_attach:
            disks_list.append(item)

    rest_data['disks'] = disks_list

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            dictionary = form.cleaned_data
            dictionary.update({'vm_id': vm_id})
            prep_data(('user/storage_image/attach/', dictionary), request.session)
            return messages_ajax.success(_('Disk has been assigned.'))
    else:
        form = form_class(rest_data=rest_data)

    return messages_ajax.success(render_to_string(template_name,
                                                  {'form': form,
                                                   'confirmation': _('Assign')},
                                                   context_instance=RequestContext(request)),
                                  status=1)
