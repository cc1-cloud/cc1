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

"""@package src.wi.utils.views

@author Krzysztof Danielowski
@author Piotr Wójcik
@date 01.04.2012
"""

from django.contrib.formtools.wizard.views import CookieWizardView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader, RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from wi.utils import CLM, check_response_errors, messages_ajax
from wi.utils.decorators import django_view
from wi.utils.messages_codes import get_error
from wi.utils.messages_ajax import ajax_request


def make_request(url, data, user=None):
    """
    """
    if not url.startswith('guest'):
        data.update({'login': user.username, 'password': user.password})

    if url.startswith('user') or url.startswith('admin_clm'):
        data.update({'cm_id': user.cm_id})
    elif url.startswith('admin_cm'):
        data.update({'cm_id': user.admin_cm_id, 'cm_password': user.cm_password})

    return CLM.send_request(url, **data)


def prep_data(request_urls, session):
    """
    Returns a dictionary of results of REST request.
    """
    data = None
    user = session.get('user')

    if request_urls is not None:
        data = {}
        # function_both is dictionary with pairs: key -> url
        if isinstance(request_urls, dict):
            for (key, val) in request_urls.iteritems():
                url = val
                args = {}
                if isinstance(val, tuple):
                    url = val[0]
                    args = val[1]
                data[key] = check_response_errors(make_request(url, args, user=user), session)['data']
        # just a simple string without any params
        elif isinstance(request_urls, str):
            data = check_response_errors(make_request(request_urls, {}, user=user), session)['data']
        # just a simple string with params as a tuple
        elif isinstance(request_urls, tuple):
            data = check_response_errors(make_request(request_urls[0], request_urls[1], user=user), session)['data']

    return data


@django_view
def direct_to_template(request, template_name, content_type=None):
    """
    Returns rendered template as HttpResponse.
    """
    context = RequestContext(request)
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context), content_type=content_type)


def simple_generic(request, template_name=None, success_msg=lambda x: '', ask_msg=lambda x: '', confirmation=_('Yes'), request_url=None, param=None):
    """
    Simple generic ajax view for creating dialogs.
    """
    return simple_generic_id(request, None, template_name, success_msg, ask_msg, confirmation, request_url, param)


def simple_generic_id(request, id1, template_name=None, success_msg=lambda x: '', ask_msg=lambda x: '',
                      confirmation=_('Yes'), request_url=None, param=None, id_key=None):
    """
    Simple generic ajax view for creating dialogs (1 entity).
    """
    return simple_generic_twoid(request, id1, None, template_name, success_msg, ask_msg, confirmation, request_url,
                                param, id_key, None)


@django_view
@ajax_request
@csrf_protect
def simple_generic_twoid(request, id1, id2, template_name=None, success_msg=lambda desc: _('Success') % {'desc': desc}, ask_msg=lambda x: '',
                         confirmation=_('Yes'), request_url=None, param=None, id_key=None, id_key2=None):
    """
    Simple generic ajax view for creating dialogs (2 entities).
    """
    if request.method == 'POST':
        if request_url is None:
            raise Exception("No 'request_url' specified.")

        args = {}
        if id1 is not None:
            if id_key is None:
                raise Exception('\'id_key\' not set in urls')
            args[id_key] = int(id1)

        if id2 is not None:
            if id_key2 is None:
                raise Exception('\'id_key2\' not set in urls')
            args[id_key2] = int(id2)

        if param is not None:
            args.update(param)

        prep_data((request_url, args), request.session)
        return messages_ajax.success(success_msg(force_escape(request.REQUEST.get('desc'))))

    if template_name is not None:
        return messages_ajax.success(render_to_string(template_name, {'text': ask_msg(force_escape(request.REQUEST.get('desc'))),
                                                                      'confirmation': confirmation, 'id': id1}, context_instance=RequestContext(request)))


def get_list_generic(request, request_url=None):
    """
    Generic ajax view returning a list.
    """
    return get_list_generic_id(request, None, request_url)


@django_view
@ajax_request
@csrf_protect
def get_list_generic_id(request, id1, request_url=None, id_key=None):
    """
    Generic ajax view returning a list.
    """
    if request.method == 'GET':
        if request_url is None:
            raise Exception("No 'request_url' specified.")

        args = {}
        if id1 is not None:
            if id_key is None:
                raise Exception('\'id_key\' not set in urls')
            args[id_key] = int(id1)

        response = prep_data((request_url, args), request.session)
        return messages_ajax.success(response)

    return messages_ajax.error('get_list_generic_id doesn\'t support POST')


def form_generic(request, template_name=None, form_class=None, request_url_post=None, request_url_get=None,
                 success_msg=lambda x: '', ask_msg=lambda x: '', confirmation=_('Yes')):
    """
    Generic ajax view for dialog handling.
    """
    return form_generic_id(request, None, template_name=template_name, form_class=form_class,
                           request_url_post=request_url_post, request_url_get=request_url_get,
                           success_msg=success_msg, ask_msg=ask_msg, confirmation=confirmation)


@django_view
@ajax_request
@csrf_protect
def form_generic_id(request, id1, template_name=None, form_class=None,
                    request_url_post=None, request_url_get=None,
                    success_msg=lambda desc: _('Success'), ask_msg=lambda x: '', confirmation=_('Yes'),
                    request_url_both=None, ajax_success_status=0, id_key=None):
    """
    Generic ajax view for dialog handling.
    """
    rest_data1 = prep_data(request_url_both, request.session)

    if request.method == 'POST':
        kwargs = {}
        if rest_data1 is not None:
            kwargs['rest_data'] = rest_data1
        form = form_class(request.POST, **kwargs)

        if form.is_valid():
            args = {}

            if id1 is not None:
                if id_key is None:
                    raise Exception('\'id_key\' not set in urls')
                args[id_key] = int(id1)
            args.update(form.cleaned_data)

            rest_data2 = prep_data((request_url_post, args), request.session)
            return messages_ajax.success(success_msg(force_escape(request.REQUEST.get('desc')), rest_data2),
                                         status=ajax_success_status)
    else:
        args = []
        kwargs = {}

        if request_url_get is not None and id1 is not None:
            response = prep_data((request_url_get, {id_key: id1}), request.session)

            args.append(response)

        if rest_data1 is not None:
            kwargs['rest_data'] = rest_data1

        form = form_class(*args, **kwargs)

    return messages_ajax.success(render_to_string(template_name, {'form': form,
                                                                  'text': ask_msg(force_escape(request.REQUEST.get('desc'))),
                                                                  'confirmation': confirmation,
                                                                  'id': id1},
                                                   context_instance=RequestContext(request)),
                                  status=1)


@django_view
@ajax_request
@csrf_protect
def generic_multiple_id(request, template_name=None, success_msg=lambda x: _('Success'),
                        ask_msg=lambda x, y: _('Do you want to?'), confirmation=_('Yes'), request_url=None, id_key=None):
    """
    Generic ajax view for handling dialogs working on multiple items.
    """
    if request.method == 'POST':
        id_list = request.POST.getlist('ids[]')

        if id_key is None:
                raise Exception('\'id_key\' not set in urls')

        if request_url is None:
            raise Exception("No 'request_url' specified.")

        response = prep_data((request_url, {id_key: [int(a) for a in id_list]}), request.session)
        if response is None:
            return messages_ajax.success(success_msg(request.POST.get('desc'), int(request.POST.get('length'))))
        return _multiple_id_return(response, id_list, request.POST.get('desc'), success_msg)
    else:
        if request.GET.get('length') is None:
            return messages_ajax.error(_("Bad argument list"))
        return messages_ajax.success(render_to_string(template_name,
                                                   {'text': ask_msg(force_escape(request.GET.get('desc')), int(request.GET.get('length'))),
                                                    'confirmation': confirmation},
                                                   context_instance=RequestContext(request)))


@django_view
@ajax_request
@csrf_protect
def generic_multiple_id_form(request, template_name=None, success_msg=lambda x: _('Success'),
                             ask_msg=lambda x, y: _('Do you want to?'),
                             confirmation=_('Yes'),
                             request_url=None, form_class=None, request_url_both=None, id_key=None):
    """
    Generic ajax view for handling dialogs working on multiple items (with a form).
    """
    response1 = prep_data(request_url_both, request.session)

    if request.method == 'POST':
        if id_key is None:
                raise Exception('\'id_key\' not set in urls')

        if request_url is None:
            raise Exception("No 'request_url' specified.")

        kwargs = {}
        if response1 is not None:
            kwargs['rest_data'] = response1
        form = form_class(request.POST, **kwargs)

        if form.is_valid():
            id_list = [int(a) for a in request.POST.getlist('ids[]')]
            dictionary = {id_key: id_list}
            dictionary.update(form.cleaned_data)
            response2 = prep_data((request_url, dictionary), request.session)

            return _multiple_id_return(response2, id_list, request.POST.get('desc'), success_msg)
    else:
        args = []
        kwargs = {}

        if response1 is not None:
            kwargs['rest_data'] = response1

        form = form_class(*args, **kwargs)

    return messages_ajax.success(render_to_string(template_name,
                                                  {'form': form,
                                                   'text': ask_msg(force_escape(request.REQUEST.get('desc')), int(request.REQUEST.get('length'))),
                                                   'confirmation': confirmation},
                                                   context_instance=RequestContext(request)),
                                 status=1)


def _multiple_id_return(response, id_list, desc, success_msg):
    """
    Helper function creating ajax response with error codes.
    """
    all_ok = True
    for machine_response in response:
        if machine_response['status'] != 'ok':
            all_ok = False
    if all_ok:
        count = len(id_list)
        return messages_ajax.success(success_msg(desc, count))
    else:
        for i in range(len(response)):
            response[i]['type'] = 'vm'
            response[i]['vmid'] = id_list[i]
            response[i]['status_text'] = unicode(get_error(response[i]['status']))
        return messages_ajax.success(response, 7999)


class CustomWizardView(CookieWizardView):
    """
    WizardView class handling browser back button after last step submition
    and skipping to 2nd step if image is already selected
    """

    wizard_name = 'custom_wizard'
    template_dir_name = 'dirname'
    url_start = 'url_start'

    def get_template_names(self):
        return self.template_dir_name + '/' + self.wizard_name + self.steps.current + '.html'

    def post(self, *args, **kwargs):
        # problem with hitting browser back button:
        # if posting on step other then the first and "step_data" in the cookie is an empty dict
        # do redirect to the first step
        if self.request.POST[self.wizard_name + '-current_step'] != '0' and self.request.COOKIES.get('wizard_' + self.wizard_name).find("\"step_data\":{}") != -1:
            return redirect(self.url_start)
        return super(CustomWizardView, self).post(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.storage.reset()

        # reset the current step to the first step.
        self.storage.current_step = self.steps.first

        # skipping first step
        if self.request.GET.get('selected_image'):
            form = self.get_form(data={'0-image_id': [self.request.REQUEST['selected_image']],
                                       self.wizard_name + '-current_step': [u'0']})
            self.storage.set_step_data(self.steps.current, self.process_step(form))

            self.storage.current_step = str(int(self.steps.first) + 1)

        return self.render(self.get_form())

    def done(self, form_list, **kwargs):
        """
        This method must be overridden by a subclass to process to form data
        after processing all steps.
        """
        raise NotImplementedError("Your %s class has not defined a done() "
            "method, which is required." % self.__class__.__name__)
