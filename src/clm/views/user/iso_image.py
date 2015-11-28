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

"""@package src.clm.views.user.iso_image
@alldecoratedby{src.clm.utils.decorators.user_log}
"""

from clm.utils.decorators import user_log, cm_request


@user_log(log=False, pack=False)
@cm_request
def get_list(cm_response, **data):
    """
    Method returns list of images.

    @clmview_user
    @cm_request_transparent{iso_image.get_list()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_by_id(cm_response, **data):  # @todo rename for fun name consistency
    """
    @clmview_user
    @cm_request_transparent{iso_image.get_by_id()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def delete(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{iso_image.delete()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def edit(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{iso_image.edit()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def download(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{iso_image.download()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def attach(cm_response, **data):  # @todo rename for fun name consistency
    """
    @clmview_user
    @cm_request_transparent{iso_image.attach()}
    """
    return cm_response


@user_log(log=True, pack=False)
@cm_request
def detach(cm_response, **data):  # @todo rename for fun name consistency
    """
    @clmview_user
    @cm_request_transparent{iso_image.detach()}
    """
    return cm_response


@user_log(log=False, pack=False)
@cm_request
def get_disk_controllers(cm_response, **data):
    """
    @clmview_user
    @cm_request_transparent{iso_image.get_disk_controllers()}
    """
    return cm_response
