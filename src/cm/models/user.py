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

"""@package src.cm.models.user

@author Maciej Nabożny <di.dijo@gmail.com>
@author Tomek Sośnicki <tom.sosnicki@gmail.com>
"""
from django.db import models
from django.db.models import Sum

from django.conf import settings
from cm.utils.exception import CMException
from cm.utils import log
from common.states import vm_states, image_states
import datetime
import calendar


class User(models.Model):
    """
    @model{USER} User's class for keeping quota.

    To have the ability to create and manage VMs and to have access to other
    CC1 features one needs to have an User account. User's general data is
    stored and proceeded on CLM and that's where User authorization and
    authentication is performed. However, User's quota differs within CM's and
    not every User has granted access to each Cluster. Thats why User class
    exists also on CM and User's quota is stored here.

    User quota is defined in "settings.py" file. It covers:
    - simultanous storage space usage,
    - simultanous CPU usage,
    - simultanous RAM memory usage,
    - IP requests count,
    - monthly points consumption.

    Points a month are calculated based on overall monthly storage, CPU, and
    RAM usage.

    By default each user gains quota speficied
    by CM settings. It may be further adjusted by admin via admin interface.
    """
    memory = models.IntegerField()
    cpu = models.IntegerField()
    storage = models.IntegerField()
    public_ip = models.IntegerField()
    points = models.IntegerField()

    class Meta:
        app_label = 'cm'

    # method for printing object instance
    def __unicode__(self):
        return str(self.id)

    @property
    def dict(self):
        """
        @returns{dict} user's data
        \n fields:
        @dictkey{id,int}
        @dictkey{cpu,int} CPU total granted by User quota
        @dictkey{memory,int} memory total [MB] granted by User quota
        @dictkey{storage,int} storage total [MB] granted by User quota
        @dictkey{public_ip,int} public IPs count total granted by User quota
        @dictkey{used_points,int} points used within current month by User
        """
        d = {}
        d['user_id'] = self.id
        d['cpu'] = self.cpu
        d['memory'] = self.memory
        d['storage'] = self.storage
        d['public_ip'] = self.public_ip
        d['used_points'] = self.used_points
        # not points, only used points?
        return d

    @property
    def long_dict(self):
        """
        @returns{dict} user's extended data in dictionary format.
        \n fields:
        @dictkey{id,int}
        @dictkey{cpu,int} CPU total granted by User quota
        @dictkey{memory,int} memory total [MB] granted by User quota
        @dictkey{storage,int} storage total [MB] granted by User quota
        @dictkey{public_ip,int} public IPs count total granted by User quota
        @dictkey{points,int} points total granted by User quota
        @dictkey{used_cpu,int} cpu currently used by User
        @dictkey{used_memory,int} memory currently used by User
        @dictkey{used_storage,int} storage currently used by User
        @dictkey{used_public_ip,int} public IPs count currently used by User
        @dictkey{used_points,int} points used within current month by User
        """
        d = {}
        d['user_id'] = self.id
        d['cpu'] = self.cpu
        d['memory'] = self.memory
        d['storage'] = self.storage
        d['public_ip'] = self.public_ip
        d['points'] = self.points
        d['used_cpu'] = self.used_cpu
        d['used_memory'] = self.used_memory
        d['used_storage'] = self.used_storage
        d['used_public_ip'] = self.public_ips.count()
        d['used_points'] = self.used_points
        return d

    @staticmethod
    def create(user_id):
        """
        Method creates and returns CM User's data. Quota is set to default
        defined in "settings.py" file.

        @parameter{user_id,int} id of the CLM User to be stored on particular CM

        @returns{User} new instance of CM User referencing to CLM user with
        given id
        """

        u = User()
        u.id = user_id  # note: id is set explicitly
        u.memory = settings.USER_QUOTA['memory']
        u.cpu = settings.USER_QUOTA['cpu']
        u.storage = settings.USER_QUOTA['storage']
        u.public_ip = settings.USER_QUOTA['public_ip']
        u.points = settings.USER_QUOTA['points']
        u.save()

        return u

    @property
    def used_cpu(self):
        """
        @returns{int} CPU being used by User the moment of call
        """
        # It sums all the cpu fields of the templates associated with the vms used by user
        c = self.vm_set.filter(state__in=[vm_states['running'], vm_states['running ctx'], vm_states['init']]).aggregate(cpu_sum=Sum('template__cpu'))

        return c['cpu_sum'] or 0

    @property
    def used_memory(self):
        """
        @returns{int} memory being used by User [MB] the moment of call
        """
        # Returns memory used by user. It sums all the memory fields of the templates associated
        # with the vms used by user
        m = self.vm_set.filter(state__in=[vm_states['running'], vm_states['running ctx'], vm_states['init']]).aggregate(memory_sum=Sum('template__memory'))

        return m['memory_sum'] or 0

    @property
    def used_storage(self):
        """
        @returns{int} storage being used by User [MB] the moment of call
        """

        # retrieve for all the images objects (sys, disk and cd) related to user (exluding images locked) the sum of their size
        # if there are no images of a type related to user, 0 is put for the sum

        return self.image_set.exclude(state__exact=image_states['locked']).aggregate(Sum('size'))['size__sum'] or 0

    @property
    def used_points(self):

        """
        @returns{int} points consumed by VMs of this User's that have been
        working within current calendar month. Those might either have been
        started the previous month and be still running during months break,
        or be just started in current month. Those may be still running or
        already closed VMs.
        """

        # Returns total points used by user. It sums all the points fields of the templates associated with the vms
        # used by user

        p = 0
        dt_now = datetime.datetime.now()
        start = datetime.datetime(dt_now.year, dt_now.month, 1)

        # next query should return all vms objects related to user (exluding vms failed, saving failed, erased)
        # with stop time>start or stop_time=none (so excluding stop_time<=start should work)
        # TODO:TEST
        vms = self.vm_set.exclude(state__in=[vm_states['failed'], vm_states['saving failed'], vm_states['erased']]).exclude(stop_time__lte=start)
        # or maybe, instead of exclude..., this:  .filter(Q(stop_time__isnull=True) | Q(stop_time__gt=start) )

        for vm in vms:
            if vm.start_time > start:
                start = vm.start_time
            t = (vm.stop_time or dt_now) - start
            if t.total_seconds() < 0:
                t = datetime.timedelta(0)
            p += vm.template.points * (t.days * 24 + t.seconds / 3600.0)
        return int(p + 0.5)

    # TODO: it works but what it does? and what it returns?
    def points_history(self):
        """
        Finds all User's VM's that have been working within current callendar
        month, which didn't fail at any stage of existence. Counts points for
        those VMs consumed within current month. Failed VMs don't count.

        @returns{dict} \n fields:
        @dictkey{points,list(list)} infos about points used in specified
        moments of time
        @dictkey{limit,int} User's quota for points per month
        """

        p = 0
        pq = []
        pts = {}
        pt = []
        vmn = 0  # vm number
        dt_now = datetime.datetime.now()
        start = datetime.datetime(dt_now.year, dt_now.month, 1)
        start_time = calendar.timegm(start.timetuple())
        now = calendar.timegm(dt_now.timetuple())

        # next query should return all vms objects related to user (exluding vms failed, saving failed, erased)
        # with stop time>start TEST or stop_time=none
        vms = self.vm_set.exclude(state__in=[vm_states['failed'],
                                             vm_states['saving failed'],
                                             vm_states['erased']]).exclude(stop_time__lte=start)

        for vm in vms:
            if vm.start_time > start:
                start = vm.start_time
            stop = vm.stop_time or dt_now

            pq.append([vmn, calendar.timegm(start.timetuple()), vm.template.points, "%s started" % (vm.name)])
            pq.append([vmn, calendar.timegm(stop.timetuple()), vm.template.points, "%s stopped" % (vm.name)])
            vmn += 1

        pq = sorted(pq, key=lambda d: d[1])

        pt.append([start_time, p, "beginning of the month"])

        for w in pq:
            for v in pts:
                p += (w[1] - pts[v][0]) / 3600.0 * pts[v][1]
                pts[v] = [w[1], pts[v][1]]
            if(w[0] in pts):
                pts.pop(w[0])
            else:
                pts.update({w[0]: [w[1], w[2]]})
            if not (w[1] in [ts[0] for ts in pt] or w[1] == now):
                pt.append([w[1], "%.4f" % p, "%s [%.0f]" % (w[3], p)])

        pt.append([now, "%.4f" % p, "now [%.0f]" % p])
        pt = sorted(pt, key=lambda d: d[0])
        return {'points': pt,
                'limit': self.points}

    def check_quota(self, template_count):
        """
        @todo Test
        template_count is a list of template objects?

        Method checks this User's quota for ability to run VMs based on
        template given and it raises CMException, if it's exceeded:

        @parameter{template_count}

        @raises{user_cpu_limit,CMException}
        @raises{user_memory_limit,CMException}
        @raises{user_storage_limit,CMException}
        @raises{user_points_limit,CMException}
        """
        cpu_sum = 0
        mem_sum = 0
        for template, count in template_count:
            cpu_sum += template.cpu * count
            mem_sum += template.memory * count
        if self.used_cpu + cpu_sum > self.cpu:
            raise CMException('user_cpu_limit')
        if self.used_memory + mem_sum > self.memory:
            raise CMException('user_memory_limit')
        if self.used_storage > self.storage:
            raise CMException('user_storage_limit')

    def check_storage(self, size):
        """
        Checks if User's storage quota is sufficient for image with given size.

        @parameter{size,int} size to fit within User's storage quota
        """
        # Add the passed size to the actual used storage to check if the sum is over the limit.
        # It raises exception in that case.

        if self.used_storage + int(size) > self.storage:
            raise CMException('user_storage_limit')

    def check_points(self):
        """
        Check if used points is over the limit
        It raises exception in that case.
        """
        if self.used_points >= self.points:
            raise CMException('user_points_limit')

    @staticmethod
    def get(user_id):
        """
        Returns the User instance by passed id.

        @parameter{user_id,int} id of the requested User

        @returns{User} instance of requested User

        @raises{user_get,CMException} cannot get user
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            log.exception(user_id, 'Cannot get user')
            raise CMException('user_get')
        return user


    # Note: superuser method moved to Admin model
