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

"""@package src.common.states
Dictionaries of the states' numbers and messages:

    - \c vm_states dictionary,
    - \c farm_states dictionary,
    - \c node_states dictionary,
    - \c vnc_states dictionary,
    - \c lease_states dictionary,
    - \c template_states dictionary,
    - \c image_type dictionary,
    - \c image_access dictionary,
    - \c image_states dictionary,
    - \c image_platforms dictionary,
    - \c filesystems dictionary,
    - \c filesystems_inv dictionary,
    - \c group_states dictionary,
    - \c cluster_states dictionary,
    - \c message_levels dictionary,
    - \c storage_states dictionary.
"""

vm_states = {'init':        0,
            'running':      1,
            'closing':      2,
            'closed':       3,
            'saving':       4,
            'failed':       5,
            'saving failed': 6,
            'running ctx':  7,
            'restart':      8,
            'suspend':      9,
            'turned off':   10,
            'erased':       11,
            'erasing':      12
            }

farm_states = {'init':        0,
               'init_head':   1,  # head is running, without ctx, wn are only in db
               'init_nodes':  2,  # head ctx called, wn are now copied
               'running':     3,
               'closing':     4,
               'closed':      5,
               'failed':      6,
               'unconfigured': 7,  # could not generate ssh key, or update hosts\
               'nodes_copied': 8,
               'saving_head': 9,
               }

node_states = {
            'init':          0,
            'ok':            1,
            'locked':        2,
            'deleted':       3,
            'storage_lock':  4,
            'offline':       5,
            }

vnc_states = {
            'detached': 0,
            'attached': 1
            }

lease_states = {
            'free': 0,
            'used': 1
            }

template_states = {
            'active': 0,
            'deleted': 1
            }

image_types = {
           'cd':        0,
           'storage':   1,
           'vm':        2
           }

image_access = {
           'private':   0,
           'public':    1,
           'group':     2
           }

image_states = {
            'ok':       0,
            'locked':   1,
            'adding':   2,
            'failed':   3,
            'unavailable':  4,
            'formatting':   5
                }

image_platforms = {
                   'unknown':   0,
                   'linux':     1,
                   'unix':      2,
                   'windows':   3,
                   'mac os':    4,
                   'other':     5
                   }

group_states = {
                'waiting':      0,
                'ok':           1,
                'not member':   2
                }

user_active_states = {
                'inactive':         0,
                'email_confirmed':  1,
                'ok':               2,
                'blocked':          3
                }

cluster_states = {
                  'ok': 0,
                  'locked': 1
                  }
message_levels = {
                 'error': 0,
                 'warn': 1,
                 'info': 2
                 }

storage_states = {
                  'ok':     0,
                  'locked': 1
                  }

ec2names = {
    'unassigned': 0,
    'm1.small': 1,
    'm1.medium': 2,
    'm1.large': 3,
    'm1.xlarge':  4,
    'm1.micro': 5,
    'c1.medium': 6,
    'c1.xlarge': 7,
    'm2.xlarge': 8,
    'm2.2xlarge': 9,
    'm2.4xlarge': 10,
    'cc1.4xlarge': 11,
    'cg1.4xlarge': 12,
}

available_network_states = {
                       'ok':        0,
                       'locked':    1,
    }

registration_states = {
                       'completed': 0,
                       'mail_confirmation': 1,
                       'admin_confirmation': 2,
                       'error': 3,
                       }

stat_resolutions = {
                     '10': 0,
                     '60': 1,  # 1 min
                     '300': 2,  # 5 min
                     '900': 3,  # 15 min
                     '3600': 4,  # 1 h
                     '86400': 5,  # 24 h
                     '604800': 6,  # 7 days
                    }

stat_names = {
               'cpu_time': 0,
               'rd_req': 1,
               'rd_bytes': 2,
               'wr_req': 3,
               'wr_bytes': 4,
               'rx_bytes': 5,
               'rx_packets': 6,
               'tx_bytes': 7,
               'tx_packets': 8,
              }

stat_ranges = {
                 '3600': 0,  # 1h
                 '21600': 1,  # 6h
                 '43200': 2,  # 12h
                 '86400': 3,  # 1 day
                 '604800': 4,  # 1 week
                 '2592000': 5,  # 1 month
                 '31536000': 6,  # 1 year
                 }

stat_units = {
              'bytes': 0,
              'time': 1,
              'ops': 2,
              'num': 3,
             }

command_states = {
    'pending':    0,
    'executing':  1,
    'failed':     2,
    'timeout':    3,
    'finished':   4
}
