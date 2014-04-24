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

"""@package src.ec2.base.action

Superclass for EC2 API actions

@author Oleksandr Gituliar <oleksandr@gituliar.org>
@copyright: Copyright (c) 2012 IFJ PAN <http://www.ifj.edu.pl/>
"""


from ec2 import lookup
from ec2.error import AuthFailure, InvalidAction, MissingParameter


class CLMException(Exception):

    def __init__(self, status, routine_name, routine_args=None):
        self.routine_args = routine_args
        self.routine_name = routine_name
        self.status = status

    def __str__(self):
        return "'%s' raised by '%s(%s)'" % \
            (self.status, self.routine_name, self.routine_args)


class Action(object):
    """Superclass for EC2 API actions."""

    def __init__(self, parameters, cluster_manager):
        self.cluster_manager = cluster_manager
        self.parameters = parameters

    def __new__(cls, parameters, cluster_manager):
        """Return an object of a concrete EC2 action class.

        Args:
            parameters <dict> of the action
            cluster_manager <ClusterManager> the action will be run at
        """
        if cls == Action:
            try:
                action = parameters['Action']
            except KeyError:
                raise MissingParameter(parameter='Action')

            found = False
            for concrete_class in cls.__subclasses__():
                if concrete_class.__name__ == action:
                    found = True
                    break
            if not found:
                raise InvalidAction(action=action)
        else:
            concrete_class = cls
        action = super(Action, cls).__new__(concrete_class, parameters, cluster_manager)
        return action

    def _get_template(self):
        name = '%s.xml' % self.parameters.get('Action')
        return lookup.get_template(name)

    def execute(self):
        """Execute EC2 action.

        This call is a wrapper around @attr{self.execute_internal} defined in the
        subclass of ect.base.action.Action.
        """

        try:
            context = self._execute() or {}
        except CLMException, error:
            if error.status == 'user_get':
                raise AuthFailure()
            raise
        template = self._get_template()
        response = template.render(**context)
        return response
