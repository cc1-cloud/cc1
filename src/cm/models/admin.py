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

"""@package src.cm.models.admin
"""
from django.db import models

from cm.models.user import User
from cm.utils.exception import CMException


class Admin(models.Model):
    """
    @model{ADMIN}

    Each Cluster may be managed by individual CM Admin, separable from overall
    cloud's Admin. This class is for Cluster Manager's Admin.
    """
    user = models.OneToOneField(User, primary_key=True)
    password = models.CharField(max_length=256)

    class Meta:
        app_label = 'cm'

    def __unicode__(self):
        return str(self.user)

    @staticmethod
    def superuser(user_id):
        """
        Method checks, whether user \c user_id is superuser.
        Otherwise it throws CMException 'user_permission'.

        @parameter{user_id,int} id of the user

        @returns{int} 1, if successful

        @raises{user_permission,CMException}
        """
        try:
            Admin.objects.get(pk=user_id)
        except:
            raise CMException('user_permission')
        return 1

    @staticmethod
    def check_password(admin_id, password_par):
        """
        Checks for *CM admin's password* correctness.

        @parameter{admin_id,int} id of the admin whose password is checked
        @parameter{password_par,string} password to check

        @raises{user_permission,CMException}
        """
        if Admin.objects.filter(user__exact=admin_id).filter(password__exact=password_par).exists():
            pass
        else:
            raise CMException('user_permission')
