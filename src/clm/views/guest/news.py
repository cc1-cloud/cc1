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

"""@package src.clm.views.guest.news
@alldecoratedby{src.clm.utils.decorators.guest_log}
@author Przemysław Syktus <syktus@gmail.com>
"""

from clm.models.news import News
from clm.utils.decorators import guest_log


@guest_log(log=False)
def get_list():
    """
    Returns list of the News.

    @clmview_guest

    @response{list(dict)} News.dicts() property for each news
    """
    news = [n.dict for n in News.objects.order_by('-date')]
    return news
