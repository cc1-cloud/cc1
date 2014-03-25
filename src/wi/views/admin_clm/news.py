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

"""@package src.wi.views.admin_clm.news
@author Krzysztof Danielowski
@author Piotr Wójcik
@date 17.03.2011
"""
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from wi.forms.news import NewsForm
from wi.utils import messages_ajax
from wi.utils.decorators import django_view
from wi.utils.messages_ajax import ajax_request
from wi.utils.views import prep_data


@django_view
@ajax_request
@csrf_protect
def mai_ajax_edit_news(request, id1, template_name='generic/form.html', form_class=NewsForm):
    """
    Ajax view for editing a news entry.
    """
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            dictionary = form.cleaned_data
            dictionary.update({'news_id': id1})
            prep_data(('admin_clm/news/edit/', dictionary), request.session)

            return messages_ajax.success(_('News entry edited.'))

    else:
        rest_data = prep_data(('admin_clm/news/get_by_id/', {'news_id': id1}), request.session)

        rest_data['sticky'] = rest_data['sticky'] != 0
        form = form_class(rest_data)

    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'text': _('Edit news data:'),
                                                                  'confirmation': _('Save'),
                                                                  'id': id1},
                                                   context_instance=RequestContext(request)),
                                  status=1)
