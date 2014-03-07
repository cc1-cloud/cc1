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

"""@package src.wi.views.admin_cm.storage_image
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 03.02.2012
"""

from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from wi.forms.user import CopyToUserForm
from wi.utils.decorators import admin_cm_permission
from wi.commontags.templatetags.templatetags import filesizeformatmb
from wi.utils import messages_ajax
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.views import prep_data


@django_view
@ajax_request
@admin_cm_permission
def cma_ajax_get_table_disks(request):
    """
    Ajax view for fetching disks list.
    """
    if request.method == 'GET':
        disks = prep_data('admin_cm/storage_image/get_list/', request.session)

        for item in disks:
            item['size'] = filesizeformatmb(item['size'])

        return messages_ajax.success(disks)


@django_view
@ajax_request
@admin_cm_permission
@csrf_protect
def cma_ajax_copy_disk(request, id1, template_name='generic/form.html', form_class=CopyToUserForm):
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

            prep_data(('admin_cm/storage_image/copy/', dictionary), request.session)

            return messages_ajax.success(_("<b>%(desc)s</b> copied.") % {'desc': force_escape(request.REQUEST.get('desc'))})
    else:
        form = form_class(rest_data=rest_data)
    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'confirmation': _('Copy'),
                                                                  'text': _('Select user:')
                                                                  },
                                                  context_instance=RequestContext(request)),
                                status=1)

