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

"""@package src.wi.views.user.key

@author Krzysztof Danielowski
@author Piotr Wójcik
"""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from wi.forms.key import GenerateKeyForm
from wi.utils import messages_ajax
from wi.utils.decorators import django_view, user_permission
from wi.utils.messages_ajax import ajax_request
from wi.utils.views import prep_data
import urllib


@django_view
@user_permission
def res_key_file(request, redirect_view='res_keys'):
    """
    View returning a file with the ssh key.
    """
    if request.method == "GET":
        if request.GET.get('name') and request.GET.get('file'):
            response = HttpResponse(content=urllib.unquote_plus(request.GET.get('file')), content_type='plain/text')
            response['Content-Disposition'] = 'attachment; filename=' + request.GET.get('name')
            return response
    return redirect(redirect_view)


@django_view
@ajax_request
@user_permission
@csrf_protect
def res_ajax_generate_key(request, template_name='generic/form.html', form_class=GenerateKeyForm):
    """
    Ajax view for ssh key generation.
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            rest_data = prep_data({'key': ('user/key/generate/', {'name': form.cleaned_data['name']})}, request.session)

            return messages_ajax.success_with_key(_("You have successfully generated a key"),
                                                   rest_data['key'],
                                                   form.cleaned_data['name'])
    else:
        form = form_class()
    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'confirmation': _('Generate'),
                                                                  'text': _('2048-bit RSA key<br /><b>Note!</b> We don\'t keep a copy of your private key. We can\'t recreate it if your key is lost.')},
                                                   context_instance=RequestContext(request)),
                                status=1)
