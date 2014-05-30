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

"""@package src.wi.utils.parsing

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 26.11.2010
"""

from django.utils.translation import ugettext as _

from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.utils.states import image_states, image_platforms_reversed, \
    ec2names_reversed


def parse_image_names(data):
    """
    Returns list of the images' names grouped by type.

    @parameter{data,dict} dictionary with keys: 'images_private', 'images_public', 'images_group'

    @returns{list} images' names.
    """
    emty_category_counter = 1
    categories = []

    categories.append([_(' '), [[-emty_category_counter, _('< Select >')]]])
    emty_category_counter += 1

    sub_categories = []

    for image in data['images_public']:
        if isinstance(image, dict) and image['state'] == image_states['ok']:
            sub_categories.append([image['image_id'], image['name']])
    if not sub_categories:
        sub_categories.append([-emty_category_counter, {'label': _('No images'), 'disabled': True}])
        emty_category_counter += 1
    public_category = [_('Public images'), sub_categories]
    categories.append(public_category)

    sub_categories = []

    for image in data['images_private']:
        if isinstance(image, dict) and image['state'] == image_states['ok']:
            sub_categories.append([image['image_id'], image['name']])
    if not sub_categories:
        sub_categories.append([-emty_category_counter, {'label': _('No images'), 'disabled': True}])
        emty_category_counter += 1
    private_category = [_('Private images'), sub_categories]
    categories.append(private_category)

    for group in data['images_group']:
        sub_categories = []
        for image in group['images']:
            if image['state'] == image_states['ok']:
                sub_categories.append([image['image_id'], image['name']])

        if not sub_categories:
            sub_categories.append([-emty_category_counter, {'label': _('No images'), 'disabled': True}])
            emty_category_counter += 1
        group_category = [_('Group') + " " + group['name'], sub_categories]
        categories.append(group_category)

    return categories


def parse_template_names(data):
    """
    Returns list of the templates' names..

    @parameter{data,dict}

    @returns{list} templates' names.
    """
    templates_list = []
    for template in data['templates']:
        if isinstance(template, dict):
            if template['ec2name'] != 0:
                templates_list.append([template['template_id'], template['name'] + ' [' + ec2names_reversed[template['ec2name']] + ']'])
            else:
                templates_list.append([template['template_id'], template['name']])
    if templates_list == []:
        templates_list.insert(0, (-1, _('None available')))
    return templates_list


def parse_ips(data, select_flag=True):
    """
    Returns list of the IPs.

    @parameter{data,dict}

    @returns{list} IPs.
    """
    ips_list = []
    all_disabled = True
    for ipa in data['ips']:
        if ipa['lease_id'] == "":
            ips_list.append([ipa['public_ip_id'], ipa['address']])
            all_disabled = False
        else:
            ips_list.append([ipa['public_ip_id'], {'label': ipa['address'], 'disabled': True}])

    if all_disabled:
        ips_list.insert(0, (-1, _('None available')))
    else:
        if select_flag == True:
            ips_list.insert(0, [-1, _('None')])
    return ips_list


def parse_ips_from_vm(data):
    """
    Returns list of the assigned IPs to selected vm.

    @parameter{data,dict}

    @returns{list} IPs.
    """
    ips_list = []
    for lease in data['vm']['leases']:
        if lease['public_ip'] != "":
            ips_list.append([lease['public_ip']['lease_id'], lease['public_ip']['ip']])
    if ips_list == []:
        ips_list.insert(0, (-1, _('None available')))
    return ips_list


def parse_leases(data):
    """
    Returns list of the assigned IPs to selected vm.

    @parameter{data,dict}

    @returns{list} IPs.
    """
    ips_list = []
    for lease in data['vm']['leases']:
        if lease['public_ip'] == "":
            ips_list.append([lease['lease_id'], lease['address']])
    if ips_list == []:
        ips_list.insert(0, (-1, _('None available')))
    return ips_list


def parse_disks(data, select_flag=True):
    """
    Returns list of the disks' names.

    @parameter{data,dict}
    @parameter{select_flag,boolean}

    @returns{list} disks' names.
    """
    disks_list = []
    all_disabled = True
    for disk in data['disks']:
        if disk['state'] == image_states['ok']:
            label = '%s (%s)' % (disk['name'], filesizeformatmb(disk['size']))
            if disk['vm_id'] == "":
                disks_list.append([disk['storage_image_id'], label])
                all_disabled = False
            else:
                disks_list.append([disk['storage_image_id'], {'label': label, 'disabled': True}])
    if disks_list == []:
        if select_flag == True:
            disks_list.append((-1, {'label': _('None available'), 'disabled': True}))
        else:
            disks_list.append((-1, _('None available')))
    else:
        if select_flag == False and all_disabled:
            disks_list.insert(0, [-1, _('None available')])

    return disks_list


def parse_disks_from_vm(data):
    """
    Returns list of the disks' names.

    @parameter{data}

    @returns{list} disks' names.
    """
    live_attach = []
    for item in data['disk_controllers']:
        if item['live_attach'] == True:
            live_attach.append(item['id'])
    disks_list = []
    all_disabled = True
    for disk in data['vm']['storage_images']:
        if disk['disk_controller'] in live_attach:
            disks_list.append([disk['storage_image_id'], disk['name']])
            all_disabled = False
        else:
            disks_list.append([disk['storage_image_id'], {'label': disk['name'], 'disabled': True}])
    if all_disabled:
        disks_list.insert(0, (-1, _('None available')))
    return disks_list


def parse_iso(data):
    """
    Returns list of the ISO images' names.

    @parameter{data}

    @returns{list} ISO images' names.
    """
    iso_list = []
    for iso in data['iso']:
        if iso['state'] == image_states['ok']:
            label = '%s (%s)' % (iso['name'], filesizeformatmb(iso['size']))
            iso_list.append([iso['iso_image_id'], label])
    if iso_list == []:
        iso_list.insert(0, (-1, _('None available')))
    else:
        iso_list.insert(0, [-1, _('None')])
    return iso_list


def parse_image_descriptions(data):
    """
    Returns list of the images' descriptions.

    @parameter{data}

    @returns{list} images' descriptions.
    """
    images_list = []

    for image in data['images_public']:
        images_list.append((image['image_id'], image['description'], image['creation_date']))

    for image in data['images_private']:
        images_list.append((image['image_id'], image['description'], image['creation_date']))

    for image in parse_group_images(data):
        images_list.append((image['image_id'], image['description'], image['creation_date']))

    return images_list


def parse_group_images(data):
    """
    Returns a list of group images.

    @parameter{data,dict}
    """
    images_group = []

    for group in data['images_group']:
        for image in group['images']:
            images_group.append(image)

    return images_group


def parse_storage_names(data):
    """
    Returns a list of the storages' names.

    @parameter{data,dict}

    @returns{list} storages' names.
    """

    storages_list = []
    if data['storages']:
        storages_list.append(('0', _('All storages')))
        for storage in data['storages']:
            if isinstance(storage, dict):
                storages_list.append((storage['storage_id'], storage['name']))
    if storages_list == []:
        storages_list.append((-1, _('None available')))

    return storages_list


def parse_node_names(data):
    """
    Returns list of the nodes' names. (attaching storage to multiple nodes).

    @parameter{data}

    @returns{list} nodes' names.
    """
    nodes_list = []
    if data['nodes']:
        nodes_list.append(('0', _('All nodes')))
        for node in data['nodes']:
            if isinstance(node, dict):
                nodes_list.append((node['node_id'], node['address']))

    if nodes_list == []:
        nodes_list.append((-1, _('None available')))

    return nodes_list


def parse_groups_ids(data):
    """
    Returns list of the groups' ids.

    @parameter{data}

    @returns{list} groups' ids.
    """
    groups_list = []

    for group in data['groups']:
        groups_list.append(group['group_id'])

    return groups_list


def parse_groups(data):
    """
    Returns list of the groups' names.

    @parameter{data}

    @returns{list} groups' names.
    """
    groups_list = []

    for group in data['groups']:
        groups_list.append([group['group_id'], group['name']])

    if groups_list == []:
        groups_list.append((-1, _('No group available')))

    return groups_list


def parse_own_groups(data):
    """
    Returns list of the ownde groups' ids.

    @parameter{data}

    @returns{list} owned groups' ids.
    """
    groups_list = []

    for group in data['own_groups']:
        groups_list.append(group['group_id'])

    return groups_list


def parse_platform():
    """
    @returns{list(key)} platforms.
    """
    platform_list = []
    for key in image_platforms_reversed:
        platform_list.append((key, image_platforms_reversed[key]))

    return platform_list


def parse_generic(data, key):
    """
    Returns a list of (potentially disabled) choices from a dictionary.
    """
    choices = []
    for k, v in sorted(data[key].iteritems(), key=lambda item: item[1]):
            choices.append([v, k])
    return choices


def parse_generic_enabled(data, key):
    """
    Returns a list of (potentially disabled) choices from a dictionary.
    """
    choices = []
    for item in data[key]:
        if item.get('enabled') is not None and not item['enabled']:
            choices.append([item['id'], {'label': item['name'], 'disabled': True}])
        else:
            choices.append([item['id'], item['name']])
    return choices


def parse_ssh_keys(data):
    """
    @parameter{data}

    @returns{list} the SSH keys.
    """
    keys_list = []
    for key in data['keys']:
        keys_list.append((key['key_id'], key['name']))

    if keys_list == []:
        keys_list.append((-1, _('None available')))

    return keys_list


def parse_cm_list(data):
    """
    @parameter{data}

    @returns{list} the CMs.
    """
    cm_list = []
    for item in data['cms']:
        cm_list.append((item['cluster_id'], item['name']))

    if cm_list == []:
        cm_list.append((-1, _('None available')))

    return cm_list


def parse_cm_users(data):
    """
    @parameter{data}

    @returns{list} the CMs' users.
    """
    cm_user_list = []
    for item in data['users']:
        cm_user_list.append((item['user_id'], item['first'] + " " + item['last']))

    if cm_user_list == []:
        cm_user_list.append((-1, _('None available')))

    return cm_user_list
