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

"""@package src.cm.models.system_image_group
"""

from django.db import models
from cm.models.system_image import SystemImage


class SystemImageGroup(models.Model):
    """
    @model{IMAGE_GROUP}
    If a system image have access=group, it has to define the group(s) to which it belongs
    The group_id is the same as the users group. Informations on users group are in the CLM.
    """
    group_id = models.IntegerField()
    image = models.ForeignKey(SystemImage)

    class Meta:
        app_label = 'cm'
        unique_together = ("group_id", "image")

    def __unicode__(self):
        return 'group: ' + str(self.group_id) + ' -  sys img: ' + str(self.image.id)
