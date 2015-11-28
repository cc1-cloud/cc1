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

"""@package src.wi.views.user.iso_image

@author Krzysztof Danielowski
@author Piotr Wójcik
"""

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.forms.iso_image import UploadISOForm
from wi.utils import messages_ajax
from wi.utils.decorators import django_view, user_permission
from wi.utils.messages_ajax import ajax_request
from wi.utils.views import prep_data


@django_view
@ajax_request
@user_permission
def res_ajax_get_iso_table(request):
    """
    Ajax view returning iso images list.
    """
    if request.method == 'GET':
        rest_data = prep_data('user/iso_image/get_list/', request.session)

        for item in rest_data:
            item['size'] = filesizeformatmb(item['size'])
        return messages_ajax.success(rest_data)


@django_view
@ajax_request
@user_permission
@csrf_protect
def res_ajax_upload_iso_http(request, template_name='generic/form.html', form_class=UploadISOForm):
    """
    Ajax view for uploading iso image from a http link.
    """
    rest_data = prep_data({'disk_controllers': 'user/iso_image/get_disk_controllers/'}, request.session)

    if request.method == 'POST':
        form = form_class(data=request.POST, rest_data=rest_data)
        if form.is_valid():
            dictionary = form.cleaned_data

            prep_data({'images': ('user/iso_image/download/', dictionary)}, request.session)

            return messages_ajax.success(_("ISO image upload started."))
    else:
        form = form_class(rest_data=rest_data)
    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'confirmation': _('Upload ISO image'),
                                                                  'text': _('Please specify ISO image parameters:')},
                                                   context_instance=RequestContext(request)),
                                status=1)

