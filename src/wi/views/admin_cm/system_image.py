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

"""@package src.wi.views.admin_cm.system_image
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.02.2012
"""

from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from common.states import image_access
from wi.forms.user import CopyToUserForm
from wi.utils.decorators import admin_cm_permission
from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.forms.system_image import AddImageHttp
from wi.utils import messages_ajax
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.states import image_states_reversed
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_table_images(request):
    """
    Ajax view for fetching images list.
    """
    if request.method == 'GET':
        rest_data = prep_data({'images_public': ('admin_cm/system_image/get_list/', {'access': image_access['public']}),
                               'images_private': ('admin_cm/system_image/get_list/', {'access': image_access['private']}),
                               'images_group': ('admin_cm/system_image/get_list/', {'access': image_access['group']})}, request.session)

        for item in rest_data['images_public']:
            item['size'] = unicode(filesizeformatmb(item['size']))
            item['type'] = 'public'
            item['stateName'] = image_states_reversed[item['state']]

        list_images = [{'name': unicode(_('Public:')), 'items': rest_data['images_public']}]

        for item in rest_data['images_private']:
            item['size'] = unicode(filesizeformatmb(item['size']))
            item['type'] = 'private'
            item['stateName'] = image_states_reversed[item['state']]

        list_images.append({'name': unicode(_('Private:')), 'items': rest_data['images_private']})

        for group in rest_data['images_group']:
            for item in group['images']:
                item['size'] = unicode(filesizeformatmb(item['size']))
                item['type'] = 'group'
                item['stateName'] = image_states_reversed[item['state']]

            list_images.append({'name': unicode(_('Group:')) + ' ' + group['name'], 'items': group['images']})

        return messages_ajax.success(list_images)


@django_view
@ajax_request
@admin_cm_permission
@csrf_protect
def cma_ajax_add_image(request, template_name='generic/form.html', form_class=AddImageHttp):
    """
    Ajax view for adding an image (http link).
    """
    rest_data = prep_data({'disk_controllers': 'user/system_image/get_disk_controllers/',
                           'video_devices':  'user/system_image/get_video_devices/',
                           'network_devices': 'user/system_image/get_network_devices/',
                          }, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            dictionary = form.cleaned_data
            prep_data({'images': ('admin_cm/system_image/download/', dictionary)}, request.session)

            return messages_ajax.success(_('You have successfully added an image.'))
    else:
        form = form_class(rest_data=rest_data)
    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'confirmation': _('Create'),
                                                                  'text': '',
                                                                  },
                                                   context_instance=RequestContext(request)),
                                status=1)


@django_view
@ajax_request
@admin_cm_permission
@csrf_protect
def cma_ajax_copy_image(request, id1, template_name='generic/form.html', form_class=CopyToUserForm):
    """
    Ajax view for changing the image owner.
    """
    rest_data = prep_data({'users': 'admin_cm/user/get_list/'}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES, rest_data=rest_data)
        if form.is_valid():
            dictionary = form.cleaned_data
            dictionary['src_image_id'] = int(id1)
            dictionary['dest_user_id'] = int(dictionary['dest_user_id'])

            prep_data(('admin_cm/system_image/copy/', dictionary), request.session)

            return messages_ajax.success(_("<b>%(desc)s</b> copied.") % {'desc': force_escape(request.REQUEST.get('desc'))})
    else:
        form = form_class(rest_data=rest_data)
    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'confirmation': _('Copy'),
                                                                  'text': _('Select user:')
                                                                  },
                                                  context_instance=RequestContext(request)),
                                status=1)
