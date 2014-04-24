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

"""@package src.clm.models.news

@author Tomek Sośnicki <tom.sosnicki@gmail.com>
@author Maciej Nabożny <di.dijo@gmail.com>
"""

from django.db import models
from clm.utils.exception import CLMException


class News(models.Model):
    """
    @model{NEWS}

    News is an entity for providing latest common News, targeted to all users,
    available on the main page of the CC1 webinterface.
    """
    ## News topic @field
    topic = models.CharField(max_length=255)
    ## News content @field
    content = models.TextField()
    ## whether this News is sticky and should be displayed for a longer time @field
    sticky = models.IntegerField()
    ## this News' publication date @field
    date = models.DateTimeField()

    class Meta:
        app_label = 'clm'

    def __unicode__(self):
        """
        @returns{string} this News topic
        """
        return self.topic

    @property
    def dict(self):
        """
        @returns{dict} this New's data
        \n fields:
        @dictkey{news_id,int} id of this News
        @dictkey{topic,string} topic of this News
        @dictkey{content,string} content of this News
        @dictkey{sticky,bool} whether this News is sticky and should be keept
        displayed for longer period
        @dictkey{date,datetime.datetime} creation date of this News
        """
        d = {}
        d['news_id'] = self.id
        d['topic'] = self.topic
        d['content'] = self.content
        d['sticky'] = self.sticky
        d['date'] = self.date
        return d

    @staticmethod
    def get(news_id):
        """
        @parameter{news_id,int} id of the requested News

        @returns{News} instance of the requested News

        @raises{news_get,CLMException} no such News found
        """
        try:
            news = News.objects.get(pk=news_id)
        except:
            raise CLMException('news_get')

        return news
