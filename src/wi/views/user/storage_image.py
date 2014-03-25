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

"""@package src.wi.views.user.storage_image
@author Krzysztof Danielowski
@author Piotr Wójcik
"""

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.forms.storage_image import AddDiskForm, UploadDiskForm
from wi.utils import messages_ajax, get_dict_from_list
from wi.utils.decorators import django_view, user_permission
from wi.utils.messages_ajax import ajax_request
from wi.utils.views import prep_data


@django_view
@ajax_request
@user_permission
def res_ajax_get_disk_table(request):
    """
    Ajax view for fetching disk list.
    """
    if request.method == 'GET':
        rest_data = prep_data({'disks': 'user/storage_image/get_list/',
                               'disk_controllers': 'user/storage_image/get_disk_controllers/'}, request.session)

        for item in rest_data['disks']:
            item['size'] = filesizeformatmb(item['size'])
            item['bus'] = get_dict_from_list(rest_data['disk_controllers'], item['disk_controller'])['name']
        return messages_ajax.success(rest_data['disks'])


@django_view
@ajax_request
@user_permission
@csrf_protect
def res_ajax_add_disk(request, template_name='resources/ajax/add_disk.html', form_class=AddDiskForm):
    """
    Ajax view for adding new disk.
    """
    rest_data = prep_data({'quota': 'user/user/check_quota/',
                           'supported_filesystems':  'user/storage_image/get_filesystems/',
                           'disk_controllers': 'user/storage_image/get_disk_controllers/'}, request.session)

    quota = rest_data['quota']

    if request.method == 'POST':
        form = form_class(request.POST, rest_data=rest_data)
        if form.is_valid():
            dictionary = form.cleaned_data

            prep_data({'key': ('user/storage_image/create/', dictionary)}, request.session)
            return messages_ajax.success(_("Disk is being created."))
    else:
        form = form_class(rest_data=rest_data)

    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'free': quota['storage'] - quota['used_storage']},
                                                   context_instance=RequestContext(request)),
                                status=1)


@django_view
@ajax_request
@user_permission
@csrf_protect
def res_ajax_upload_disk_http(request, template_name='generic/form.html', form_class=UploadDiskForm):
    """
    Ajax view for uploading image from a http link.
    """
    rest_data = prep_data({'disk_controllers': 'user/storage_image/get_disk_controllers/'}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            dictionary = form.cleaned_data

            prep_data({'images': ('user/storage_image/download/', dictionary)}, request.session)
            return messages_ajax.success(_("Disk upload started."))
    else:
        form = form_class(rest_data=rest_data)
    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'confirmation': _('Upload disk'),
                                                                  'text': _('Please specify disk parameters:')},
                                                   context_instance=RequestContext(request)),
                                status=1)
