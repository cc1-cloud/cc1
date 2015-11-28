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

"""@package src.clm.views.admin_clm.news

@alldecoratedby{src.clm.utils.decorators.admin_clm_log}
"""

from clm.models.news import News
from clm.utils.exception import CLMException
from datetime import datetime
from clm.utils.decorators import admin_clm_log


@admin_clm_log(log=True)
def get_by_id(cm_id, caller_id, news_id):
    """
    @clmview_admin_clm
    @param_post{news_id}
    @response{dict} dict property of the requested News
    """
    return News.get(news_id).dict


@admin_clm_log(log=True)
def add(cm_id, caller_id, topic='', content='', sticky=False):
    """
    Creates and saves new News. Such a News appears on the Web Interface's
    home screen.

    @clmview_admin_clm
    @param_post{topic,string}
    @param_post{content,string}
    @param_post{sticky,bool} whether the News should stay displayed long-term
    """

    news = News()
    news.topic = topic
    news.content = content
    news.sticky = sticky
    news.date = datetime.now()

    try:
        news.save()
    except:
        raise CLMException('news_create')


@admin_clm_log(log=True)
def delete(cm_id, caller_id, news_id):
    """
    Deletes permanently specified News. Deleted News can i no way be
    recovered.

    @clmview_admin_clm
    @param_post{news_id,int} id of the News to delete
    """
    news = News.get(news_id)
    try:
        news.delete()
    except CLMException, e:
        raise e
    except Exception, e:
        raise CLMException('news_delete')


@admin_clm_log(log=True)
def edit(cm_id, caller_id, news_id, topic=None, content=None, sticky=None):
    """
    @clmview_admin_clm
    @param_post{news_id,int} id of the News to edit
    @param_post{topic,string} new topic of the News
    @param_post{content,string} new content of the News
    @param_post{sticky,bool} whether the News should stay displayed long-term
    """
    news = News.get(news_id)
    if topic:
        news.topic = topic
    if content:
        news.content = content
    if sticky is not None:
        news.sticky = sticky
    try:
        news.save()
    except:
        raise CLMException('news_edit')
