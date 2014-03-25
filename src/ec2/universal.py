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
from ec2.base.action import Action
from ec2.error import MissingParameter, InvalidAMIID, InvalidParameterValue

"""@package src.ec2.universal
EC2 actions common for more than one resource
@copyright Copyright (c) 2014 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


class CreateTags(Action):
    def _execute(self):
        resource_ids = []
        tags = []
        try:
            for param, value in self.parameters.iteritems():
                if param.startswith('ResourceId'):
                    resource_ids.append(value)
                elif param.startswith('Tag.') and param.endswith('Key'):
                    tag_value = self.parameters.get('Tag.' + param[4:-4] + '.Value')
                    if value != 'Name':
                        raise InvalidParameterValue
                    tags.append({'Name': tag_value})
        except KeyError:
            raise MissingParameter(parameter='ImageId') # TODO
        except ValueError:
            #raise InvalidAMIID.NotFound(image_id=image_id)
            raise InvalidAMIID.Malformed # TODO
        
        
        for resource in resource_ids:
            if resource.startswith('vol-'):
#                 (caller_id, storage_image_id, name, description, disk_controller):
                for tag in tags:
                    volume = self.cluster_manager.user.storage_image.get_by_id({'storage_image_id':resource[4:]})
                    if not volume:
                        pass # TODO 
                    
                    self.cluster_manager.user.storage_image.edit({'storage_image_id':resource[4:],
                                                              'name' : tag['Name'],
                                                              'description' : volume['description'],
                                                              'disk_controller' : volume['disk_controller']})
            elif resource.startwith('i-'):
                pass
            else:
                raise InvalidParameterValue
            
        # we don't return anything, in this point the only value might be True and it's coded within template
        



