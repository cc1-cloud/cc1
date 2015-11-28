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

"""@package src.clm.models.cluster
@author Miłosz Zdybał <milosz.zdybal@ifj.edu.pl>
"""

from django.db import models
from clm.utils.exception import CLMException
from common.states import cluster_states


class Cluster(models.Model):
    """
    @model{CLUSTER}

    Cluster is set of virtualization Nodes connected within single network.
    """
    ## network address of the Cluster @field
    address = models.CharField(max_length=20)
    ## port on which Cluster is running @field
    port = models.IntegerField()
    ## human-readable name of the Cluster (one that is displayed in web interface) @field
    name = models.CharField(max_length=40, unique=True)
    ## whether cluster is available or locked, @seealso{src.common.states.cluster_states} @field
    state = models.IntegerField()

    class Meta:
        app_label = 'clm'

    def __unicode__(self):
        return self.name

    @property
    def dict(self):
        """
        @returns{dict} this Cluster's data
        \n fields:
        @dictkey{cluster_id,int} id of this Cluster
        @dictkey{address,string} address of the this Cluster
        @dictkey{port,int} port on which this Cluster works
        @dictkey{name,string} name of the this Cluster
        @dictkey{state,int} state of the this Cluster, whether it's available or locked, @seealso{src.common.states.cluster_states}
        """
        d = {}
        d['cluster_id'] = self.id
        d['address'] = self.address
        d['port'] = self.port
        d['name'] = self.name
        d['state'] = self.state
        return d

    @property
    def short_dict(self):
        """
        @returns{dict} this Cluster's shortened data
        \n fields:
        @dictkey{cluster_id,int} id of this Cluster
        @dictkey{name,string} name of the this Cluster
        @dictkey{state,int} state of the this Cluster, @seealso{src.common.states.cluster_states}
        """
        d = {}
        d['cluster_id'] = self.id
        d['name'] = self.name
        d['state'] = self.state
        return d

    @staticmethod
    def get(cluster_id):
        """
        @parameter{cluster_id,int} id of the requested Cluster
        @returns{Cluster} instance of the requested Cluster

        @raises{cluster_get,CLMException} no such Cluster
        @raises{cluster_locked,CLMException} Cluster is locked
        """
        try:
            cluster = Cluster.objects.get(pk=cluster_id)
        except Cluster.DoesNotExist:
            raise CLMException('cluster_get')
        if cluster.state == cluster_states['locked']:
            raise CLMException('cluster_locked')

        return cluster
