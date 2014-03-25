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

"""@package src.wi.utils.states
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 8.6.2010

Module contains dictionaries translating between states and numbers.
"""

from django.utils.translation import ugettext_lazy as _

from common.states import vm_states, node_states, image_access, image_types, \
    image_platforms, image_states, message_levels, ec2names, \
    cluster_states as cm_active, storage_states, \
    available_network_states as pool_states

farm_states_reversed = {
                       0: _('Copying farm\'s head'),
                       1: _('Waiting for head\'s contextualization'),
                       2: _('Copying Worker Nodes'),
                       3: _('Running'),
                       4: _('Closing'),
                       5: _('Closed'),
                       6: _('Failed'),
                       7: _('Unconfigured'),
                       8: _('Configuring'),
                       9: _('Saving head')
                      }

farm_descriptions_reversed = {
                       0: _('Farm\'s head is beeing copied, this could take a while depending on the image size'),
                       1: _('Waiting for head\'s contextualization. If the head\'s OS is running, but the farm remains in this state, this could indicate problem with contextualization. Image without contextualization can not be used to create farm. If this is a case please destroy the farm.'),
                       2: _('Worker Nodes are beeing copied, this could take a while depending on the image size'),
                       3: _('Farm is running'),
                       4: _('Closing'),
                       5: _('Closed'),
                       6: _('Farm failed'),
                       7: _('Farm could not be configured, passwordless communication between Head and WN is not guaranteed, the configuration script probably will not work correctly, you can still configure farm manually'),
                       8: _('Configuring worker nodes and waiting for contextualization'),
                       9: _('Saving farm\'s head')
                      }

network_types_reversed = {
                       0: _('private'),
                       1: _('public'),
                       }

user_active_reversed = {
                       0: _('inactive'),
                       1: _('email confirmed'),
                       2: _('active'),
                       3: _('blocked'),
                       }

user_groups_states_reversed = {
                               0: _('pending'),
                               1: _('member'),
                               2: _('not a member'),
                               }

vm_states_reversed = dict((v, k) for k, v in vm_states.iteritems())

cm_active_reversed = dict((v, k) for k, v in cm_active.iteritems())

node_states_reversed = dict((v, k) for k, v in node_states.iteritems())

storage_states_reversed = dict((v, k) for k, v in storage_states.iteritems())

image_access_reversed = dict((v, k) for k, v in image_access.iteritems())

image_types_reversed = dict((v, k) for k, v in image_types.iteritems())

image_platforms_reversed = dict((v, k) for k, v in image_platforms.iteritems())

image_states_reversed = dict((v, k) for k, v in image_states.iteritems())

message_levels_reversed = dict((v, k) for k, v in message_levels.iteritems())

pool_states_reversed = dict((v, k) for k, v in pool_states.iteritems())

ec2names_reversed = dict((v, k) for k, v in ec2names.iteritems())

stat_names_reversed = {
                       0: _('CPU time'),
                       1: _('HDD read IO'),
                       2: _('HDD read bytes'),
                       3: _('HDD write IO'),
                       4: _('HDD write bytes'),
                       5: _('Network received bytes'),
                       6: _('Network received packets'),
                       7: _('Network sent bytes'),
                       8: _('Network sent packets'),
                      }

stat_short_names_reversed = {
                       0: 'cpu_time',
                       1: 'rd_req',
                       2: 'rd_bytes',
                       3: 'wr_req',
                       4: 'wr_bytes',
                       5: 'rx_bytes',
                       6: 'rx_packets',
                       7: 'tx_bytes',
                       8: 'tx_packets',
                      }

stat_resolutions_reversed = {
                             0: _('10 s'),
                             1: _('60 s'),
                             2: _('5 m'),
                             3: _('15 m'),
                             4: _('1 h'),
                             5: _('1 day'),
                             6: _('1 week'),
                            }

stat_ranges_reversed = {
                         0: _('1 hour'),
                         1: _('6 hours'),
                         2: _('12 hours'),
                         3: _('1 day'),
                         4: _('1 week'),
                         5: _('1 month'),
                         6: _('1 year'),
                       }
