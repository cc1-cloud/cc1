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

"""@package src.cm.views.user.admin

@alldecoratedby{src.cm.utils.decorators.user_log}
"""

from cm.utils.exception import CMException
from cm.utils.decorators import user_log, admin_cm_log
from cm.models.admin import Admin
from cm.models.user import User
from cm.utils import log


# The new admin is the user who calls the function, that is the CLM admin who creates the new cluster
@user_log(log=True)
def first_admin_add(caller_id, new_password, clm_address):
    """
    Method creates first admin of the cluster.
    It should be called after confirmation of the CLM admin form for
    adding new CM. System cannot work with no CM admin existing.
    @cmview_user

    @note Method can be run only if no CM admin exists in the CM database.

    @parameter{password,string} first *CM admin password* to set
    """
    user = User.create(1)
    user.save()

    # creates a new admin, which is the caller
    admin = Admin()
    admin.user = user
    admin.password = new_password

    try:
        admin.save()
    except:
        raise CMException('admin_add')

    # Update config and setup CLM address
    try:
        lines = []
        config = open('/usr/lib/cc1/cm/config.py', 'r')
        for line in config.readlines():
            if line.startswith('CLM_ADDRESS') and 'NOT_CONFIGURED' in line:
                lines.append('CLM_ADDRESS = "https://%s:8000/"\n' % clm_address)
            else:
                lines.append(line)
        config.close()

        config = open('/usr/lib/cc1/cm/config.py', 'w')
        config.write(''.join(lines))
        config.close()
    except:
        log.exception(caller_id, 'config_update')
        raise CMException('config_update')


# never used
@admin_cm_log(log=True)
def check_password(caller_id):
    """
    @parameter{caller_id}
    @cmview_admin_cm

    View's decorator checks password. Therefore check_password()
    doesn't need to perform any further check.
    @decoratedby{src.cm.utils.decorators.admin_cm_log}
    """
    pass
