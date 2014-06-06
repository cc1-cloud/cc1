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

"""@package src.wi.views.user.farm

@author Piotr Wójcik
@date 14.11.2011
"""

from colorsys import hsv_to_rgb

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from wi.utils import messages_ajax, parsing
import wi.utils as utils
from wi.utils.decorators import django_view, user_permission
from wi.utils.exceptions import RestErrorException
from wi.utils.formatters import time_from_sec
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import farm_states_reversed as farm_states, \
    vm_states_reversed, farm_descriptions_reversed as farm_states_help
from wi.utils.views import prep_data, CustomWizardView


class CreateFarmWizard(CustomWizardView):
    """
    Form wizard for farm creation.
    """
    url_done = 'far_show_farm'
    url_start = 'far_create_farm'

    wizard_name = 'create_farm_wizard'
    template_dir_name = 'farms'

    def done(self, form_list, **kwargs):
        """
        Action executed on last step submition.
        """
        form_data = self.get_all_cleaned_data()
        try:
            prep_data({'farm': ('user/farm/create/', form_data)}, self.request.session)
        except RestErrorException as ex:
            messages.error(self.request, ex.value)
        else:
            messages.success(self.request, _('Farm is being created.'))

        return redirect(self.url_done)

    def get_form_kwargs(self, step=None):
        step = int(step)
        initial_data = {}

        if step == 1:
            rest_data = prep_data({'templates': 'user/template/get_list/'}, self.request.session)
            initial_data = {'rest_data': rest_data,
                            'session': self.request.session}

        if step == 2:
            rest_data = prep_data({'ips': 'user/public_ip/get_list/',
                                   'disks': 'user/storage_image/get_list/',
                                   'iso': 'user/iso_image/get_list/',
                                  }, self.request.session)
            initial_data = {'rest_data': rest_data}

        return initial_data

    def get_context_data(self, form, **kwargs):
        context = super(CreateFarmWizard, self).get_context_data(form=form, **kwargs)
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

        elif self.steps.current == '1':
            form_cleaned_data = self.get_all_cleaned_data()
            rest_data = prep_data({'image': ('user/system_image/get_by_id/', {'system_image_id': form_cleaned_data['image_id']}),
                                   }, self.request.session)

            context.update({'steps_desc': [rest_data['image']['name'] if len(rest_data['image']['name']) <= 15 else rest_data['image']['name'][:15] + '...', _('Hardware'), _('Optional resources'), _('Summary')]})

        elif self.steps.current == '2':
            form_cleaned_data = self.get_all_cleaned_data()
            rest_data = prep_data({'image': ('user/system_image/get_by_id/', {'system_image_id': form_cleaned_data['image_id']}),
                                   'templates': 'user/template/get_list/',
                                   }, self.request.session)
            template = utils.get_dict_from_list(rest_data['templates'], form_cleaned_data['worker_template_id'], key='template_id')
            context.update({'steps_desc': [rest_data['image']['name'] if len(rest_data['image']['name']) <= 15 else rest_data['image']['name'][:15] + '...', str(form_cleaned_data['count']) + ' * ' + str(template['cpu']) + '/' + str(template['memory']), _('Optional resources'), _('Summary')]})

        elif self.steps.current == '3':
            form_cleaned_data = self.get_all_cleaned_data()
            rest_data = prep_data({'image': ('user/system_image/get_by_id/', {'system_image_id': form_cleaned_data['image_id']}),
                                   'templates': 'user/template/get_list/',
                                   'ips': 'user/public_ip/get_list/',
                                   'disks': 'user/storage_image/get_list/',
                                   'iso': 'user/iso_image/get_list/',
                                   }, self.request.session)
            summary_data = {'summary_image': rest_data['image'],
                            'summary_head_template': utils.get_dict_from_list(rest_data['templates'], form_cleaned_data['head_template_id'], key='template_id'),
                            'summary_template': utils.get_dict_from_list(rest_data['templates'], form_cleaned_data['worker_template_id'], key='template_id'),
                            'summary_count': form_cleaned_data['count'],
                            'summary_ip': utils.get_dict_from_list(rest_data['ips'], form_cleaned_data['public_ip_id'], key='public_ip_id'),
                            'summary_disks': utils.get_dicts_from_list(rest_data['disks'], form_cleaned_data['disk_list'], key='storage_image_id'),
                            'summary_iso': utils.get_dicts_from_list(rest_data['iso'], form_cleaned_data['iso_list'], key='iso_image_id'),
                            'summary_vnc': form_cleaned_data['vnc'],
                            }

            template = utils.get_dict_from_list(rest_data['templates'], form_cleaned_data['worker_template_id'], key='template_id')
            context.update({'steps_desc': [rest_data['image']['name'] if len(rest_data['image']['name']) <= 15 else rest_data['image']['name'][:15] + '...', str(form_cleaned_data['count']) + ' * ' + str(template['cpu']) + '/' + str(template['memory']), _('Optional resources'), _('Summary')]})

            context.update(summary_data)

        return context


CreateFarmWizard.dispatch = method_decorator(user_permission)(
                            method_decorator(django_view)(
                                CreateFarmWizard.dispatch))


@django_view
@ajax_request
@user_permission
def far_ajax_get_table(request):
    """
    Ajax view for fetching farm list.
    """
    if request.method == 'GET':
        rest_data = prep_data('user/farm/get_list/', request.session)

        for item in rest_data:
            item['uptime'] = time_from_sec(item['uptime'])
            item['stateName'] = unicode(farm_states[item['state']])
            item['stateTooltip'] = unicode(farm_states_help[item['state']])

            for vm in item['vms']:
                vm['stateName'] = unicode(vm_states_reversed[vm['state']])
                vm['pub_ip'] = []
                for i in vm['leases']:
                    if i['public_ip'] != "":
                        vm['pub_ip'].append(i['public_ip']['address'])

                vm['priv_ip'] = []
                for i in vm['leases']:
                    vm['priv_ip'].append(i['address'])

                vm['cpuLoadPercent'] = int(min(float(vm['cpu_load'].get('60') or 0) * 100, 100))
                vm['cpuLoadColor'] = "#%02x%02x%02x" % tuple(i * 255 for i in hsv_to_rgb(float(vm['cpuLoadPercent']) / 300, 1.0, 0.8))

        return messages_ajax.success(rest_data)
