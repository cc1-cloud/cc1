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

"""@package src.wi.views.user.system_image
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 3.1.2011
"""

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from common.states import image_access, image_states
from wi.utils.decorators import user_permission
from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.forms.system_image import AddImageHttp
from wi.utils import messages_ajax, parsing
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import image_states_reversed
from wi.utils.views import prep_data


@django_view
@ajax_request
@user_permission
def img_ajax_get_private_table(request):
    """
    Ajax view for fetching user's private images list.
    """
    if request.method == 'GET':
        rest_data = prep_data({'images_private': ('user/system_image/get_list/', {'access': image_access['private']}),
                               'images_group': ('user/system_image/get_list/', {'access': image_access['group']})}, request.session)

        for item in rest_data['images_private']:
            item['stateName'] = image_states_reversed[item['state']]
            item['type'] = 'private'
            item['size'] = filesizeformatmb(item['size'])

        group_list = [{'name': unicode(_('Private')), 'items': rest_data['images_private']}]

        for group in rest_data['images_group']:
            group_images_list = []
            for item in group['images']:
                if item['user_id'] == request.session['user'].user_id:
                    item['stateName'] = image_states_reversed[item['state']]
                    item['size'] = unicode(filesizeformatmb(item['size']))
                    item['type'] = 'group'
                    group_images_list.append(item)

            group_list.append({'name': unicode(_('Shared to group')) + ' ' + group['name'],
                                'items': group_images_list, 'group_id': group['group_id']})

        return messages_ajax.success(group_list)


@django_view
@ajax_request
@user_permission
def img_ajax_get_public_table(request):
    """
    Ajax view for fetching public images list.
    """
    if request.method == 'GET':
        rest_data = prep_data(('user/system_image/get_list/', {'access': image_access['public']}), request.session)

        for item in rest_data:
            item['stateName'] = image_states_reversed[item['state']]
            item['size'] = filesizeformatmb(item['size'])

        return messages_ajax.success(rest_data)


@django_view
@ajax_request
@user_permission
def img_ajax_get_group_table(request):
    """
    Ajax view for fetching group images list.
    """
    if request.method == 'GET':
        rest_data = prep_data({'own_groups': 'user/group/list_own_groups/',
                               'group_images': ('user/system_image/get_list/', {'access': image_access['group']}),
                              }, request.session)

        leader = parsing.parse_own_groups(rest_data)

        group_list = []
        for group in rest_data['group_images']:

            group_images_list = []
            for item in group['images']:
                item['stateName'] = unicode(image_states_reversed[item['state']])
                item['size'] = filesizeformatmb(item['size'])
                item['mine'] = True if item['user_id'] == request.session['user'].user_id else False
                item['myGroup'] = True if item['group_id'] in leader else False
                group_images_list.append(item)

            group_list.append({'name': group['name'], 'items': group_images_list, 'group_id': group['group_id']})
        return messages_ajax.success(group_list)


@django_view
@ajax_request
@user_permission
@csrf_protect
def img_ajax_add_image_http(request, template_name='generic/form.html', form_class=AddImageHttp):
    """
    Ajax view for handling adding image from http link.
    """
    rest_data = prep_data({'disk_controllers': 'user/system_image/get_disk_controllers/',
                           'video_devices':  'user/system_image/get_video_devices/',
                           'network_devices': 'user/system_image/get_network_devices/'
                          }, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES, rest_data=rest_data)
        if form.is_valid():
            dictionary = form.cleaned_data

            prep_data(('user/system_image/download/', dictionary), request.session)
            return messages_ajax.success(_('Image upload started.'))
    else:
        form = form_class(rest_data=rest_data)
    return messages_ajax.success(render_to_string(template_name,
                                                  {'form': form,
                                                   'confirmation': _('Add image'),
                                                    'text': _('Please specify image parameters:')},
                                                   context_instance=RequestContext(request)),
                                status=1)


@django_view
@ajax_request
@user_permission
def img_ajax_get_all_table(request, img_type):
    """
    Ajax view fetching image list.
    all         = ALL
    private     = My images
    public      = Public
    1 ... x     = Group
    """
    if request.method == 'GET':
        rest_data = prep_data({'images_private': ('user/system_image/get_list/', {'access': image_access['private']}),
                               'images_public': ('user/system_image/get_list/', {'access': image_access['public']}),
                               'images_group': ('user/system_image/get_list/', {'access': image_access['group']})
                              }, request.session)
        list_images = []

        if img_type == 'private' or img_type == 'all':
            for item in rest_data['images_private']:
                if item['state'] != image_states['ok']:
                    continue
                item['stateName'] = image_states_reversed[item['state']]
                item['type'] = _('private')
                item['size'] = filesizeformatmb(item['size'])
                list_images.append(item)

        if img_type == 'public' or img_type == 'all':
            for item in rest_data['images_public']:
                if item['state'] != image_states['ok']:
                    continue
                item['stateName'] = image_states_reversed[item['state']]
                item['type'] = _('public')
                item['size'] = filesizeformatmb(item['size'])
                list_images.append(item)

        if img_type == 'all':
            for group in rest_data['images_group']:
                for item in group['images']:
                    if item['state'] != image_states['ok']:
                        continue
                    item['stateName'] = image_states_reversed[item['state']]
                    item['size'] = unicode(filesizeformatmb(item['size']))
                    item['type'] = _('group ') + group['name']
                    list_images.append(item)

        if img_type != 'public' and img_type != 'private' and img_type != 'all':
            for group in rest_data['images_group']:
                if (img_type == str(group['group_id'])):
                    for item in group['images']:
                        if item['state'] != image_states['ok']:
                            continue
                        item['stateName'] = image_states_reversed[item['state']]
                        item['size'] = unicode(filesizeformatmb(item['size']))
                        item['type'] = _('group ') + group['name']
                        list_images.append(item)

        if img_type == 'private':
            for group in rest_data['images_group']:
                for item in group['images']:
                    if img_type == 'private' and item['user_id'] == request.session['user'].user_id:
                        if item['state'] != image_states['ok']:
                            continue
                        item['stateName'] = image_states_reversed[item['state']]
                        item['size'] = unicode(filesizeformatmb(item['size']))
                        item['type'] = _('group ') + group['name']
                        list_images.append(item)

        return messages_ajax.success(list_images)
