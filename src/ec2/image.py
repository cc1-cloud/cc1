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
from common.states import image_access, image_types, image_states, group_states
from ec2.base.action import Action, CLMException
from ec2.error import InvalidAMIID, MissingParameter, InternalError, \
    UndefinedError, InvalidParameterValue, InvalidFilter
from ec2.helpers.entities import Entity
from ec2.helpers.filters import applyEc2Filters, validateEc2Filters
from ec2.helpers.parse import parseFilters, parseID, parseIDs

"""@package src.ec2.image
EC2 actions for images

@copyright Copyright (c) 2012 Institute of Nuclear Physics PAS <http://www.ifj.edu.pl/>
@author Rafał Grzymkowski
@author Oleksandr Gituliar <gituliar@gmail.com>
@author Miłosz Zdybał
@author Łukasz Chrząszcz <l.chrzaszcz@gmail.com>
"""


# Use windows if you have Windows based AMIs; otherwise leave blank.
# Type: String
# Valid Value: windows
PLATFORM = {
    0: '',           # unknown
    1: '',           # linux
    2: '',           # unix
    3: 'windows',    # windows
    4: '',           # mac os
    5: '',           # other
}

# State of the image.
# Type: String
# Valid Values: available | pending | failed
STATE = {
    0: 'available',  # ok
    1: 'failed',     # locked
    2: 'pending',    # adding
    3: 'failed',     # failed
    4: 'failed',     # unavailable
}


class DeregisterImage(Action):
    def _execute(self):
        try:
            image_id = parseID(self.parameters['ImageId'], Entity.image)
            if not image_id:
                raise InvalidParameterValue
            image_id = int(image_id)
        except KeyError:
            raise MissingParameter(parameter='ImageId')
        except ValueError:
            raise InvalidAMIID.Malformed

        try:
            none = self.cluster_manager.user.system_image.delete({'system_image_id':image_id})
        except CLMException, error:
            if error.status == 'image_get' or error.status == 'image_unavailable':
                raise InvalidAMIID.NotFound(image_id=image_id)
            if error.status == 'image_delete':
                raise InternalError
            raise UndefinedError

        return {'result': 'true'}


class DescribeImages(Action):

    available_filters = ['description', 'image-id', 'name', 'state']

    def _execute(self):
        GROUP_ACCESS = image_access['group']
        PRIVATE_ACCESS = image_access['private']
        PUBLIC_ACCESS = image_access['public']

        filters = parseFilters( self.parameters )
        if not validateEc2Filters( filters, self.available_filters ):
            raise InvalidFilter

        image_ids = []
        for param, value in self.parameters.iteritems():
            if param.startswith('ImageId'):
                image_id = parseID(value, Entity.image)
                if not image_id:
                    raise InvalidParameterValue
                image_ids.append( image_id )

        images = []
        for access in (PRIVATE_ACCESS, PUBLIC_ACCESS):

            access_images = self.cluster_manager.user.system_image.get_list({
                'access': access,
            })


            for image in access_images:
                if image_ids and str(image.get('image_id')) not in image_ids:
                    continue
                images.append({
                    'description': image.get('description').replace('<', ' '),
                    'image-id': image.get('image_id'),
                    'is_public': 'true' if access == PUBLIC_ACCESS else 'false',
                    'name': image['name'],
                    'owner_id': image.get('user_id'),
                    'platform': PLATFORM.get(image.get('platform')),
                    'state': STATE.get(image.get('state')),
                })

        # listowanie obrazów grupowych - one są zwracane w innej strukturze
        access_images = self.cluster_manager.user.system_image.get_list({'access': GROUP_ACCESS})


        for images_dict in access_images:
            for image in images_dict['images']:
                if image_ids and str(image.get('image_id')) not in image_ids:
                    continue
                images.append({
                    'description': image.get('description').replace('<', ' '),
                    'image-id': image.get('image_id'),
                    'is_public': 'true' if access == PUBLIC_ACCESS else 'false',
                    'name': image['name'],
                    'owner_id': image.get('user_id'),
                    'platform': PLATFORM.get(image.get('platform')),
                    'state': STATE.get(image.get('state')),
                })

        if filters.get('state'):
            for state in filters['state']:
                state = [k for k,v in STATE.iteritems() if v == STATE.get(state) ] # ?? wymaga testu
            del filters['state']

        images = applyEc2Filters( images, filters )
# filtry TODO:
# is-public

        return {'images': images}
