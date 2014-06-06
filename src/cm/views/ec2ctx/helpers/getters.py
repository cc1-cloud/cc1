# _*_ coding: utf_8 _*_
# @COPYRIGHT_begin
#
# Copyright [2010_2013] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE_2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end

"""@package src.cm.manager.ec2ctx.helpers.getters

@copyright Copyright (c) 2013 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


def get_exposed_methods(exposed_class):
    command_list = [command for command in dir(exposed_class) if hasattr(getattr(exposed_class, command), "exposed") and getattr(exposed_class, command).exposed == True]
    return command_list


def remove_index(lista):
    del lista[ lista.index('index') ]
    return lista


def switch_to_hyphens(lista):
    return [sub_method.replace("_", "-") for sub_method in lista]


def get_submethods(exposed_class):
    return switch_to_hyphens(remove_index(get_exposed_methods(exposed_class)))
