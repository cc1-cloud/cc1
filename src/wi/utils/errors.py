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

"""@package src.wi.utils.errors
"""

import logging

from django.template.defaultfilters import force_escape
from django.utils.translation import ugettext_lazy as _


auth_error_text = _('Authorization error. Re-login required.')


def get_error(error_key):
    """
    If error with \c error_key exists, function returns it's message. Otherwise it returns "*Unknown error :(*" message.
    """
    # # \c errors - dictionary of the errors <b>informations' keys</b> and <b>information</b>
    #  (for error informations without parameters):
    #  - CLM ERRORS dictionary
    #  - CM ERRORS dictionary

    errors = {
        'ok':                        _('No error'),
    #===============================================================================
    # CLM ERRORS
    #===============================================================================
        'clm_error':                 _('Server error.'),

        'cluster_add':               _('Error: adding cluster failed.'),
        'cluster_add_admin':         _('Error: adding admin to cluster failed.'),
        'cluster_add_users':         _('Error: adding users to cluster failed.'),
        'cluster_edit':              _('Error: editing cluster failed.'),
        'cluster_get':               _('Error: invalid Cluster Manager - please login again.'),
        'cluster_lock':              _('Error: locking cluster failed.'),
        'cluster_unlock':            _('Error: unlocking cluster failed.'),

        'group_change_owner':        _('Error: changing leader failed.'),
        'group_create':              _('Error: creating group failed.'),
        'group_get':                 _('Error: group not found.'),
        'group_delete':              _('Error: deleting group failed.'),
        'group_delete_user':         _('Error: deleting user from group failed.'),
        'group_edit':                _('Error: editing group failed.'),

        'news_create':               _('Error: creating news failed.'),
        'news_delete':               _('Error: deleting news failed.'),
        'news_edit':                 _('Error: editing news failed.'),
        'news_get':                  _('Error: news not found.'),

        'reset_password_error':      _('Error: mailing server is not active.'),
        'reset_password_smtp_error': _('Error: sending email.'),
        'send_issue_error':          _('Error: sending email to administrator.'),

        'ssh_key_already_exist':     _('Error: ssh key already exist.'),
        'ssh_key_format':            _('Error: invalid format.'),
        'ssh_key_generate':          _('Error: generating key failed.'),
        'ssh_key_get':               _('Error: key not found.'),
        'ssh_key_limit':             _('Error: key limit.'),

        'user_activate':             _('Error: activating user failed.'),
        'user_active':               _('Error: deleting user account.'),
        'user_block':                _('Error: blocking user failed.'),
        'user_delete':               _('Error: deleting user failed.'),
        'user_edit':                 _('Error: editing user data failed.'),
        'user_get':                  _('Error: user not found.'),
        'user_inactive':             _("Error: user account isn't activated."),
        'user_not_in_group':         _("Error: user doesn't belong to this group."),
        'user_permission':           _('Error: you have no permissions.'),
        'user_register':             _('Error: registering user failed.'),
        'user_set_admin':            _('Error: setting admin failed.'),
        'user_set_password':         _('Error: setting password failed.'),
        'user2group_get':            _('Error: request for this group not found.'),
        'user_state':                _('Error: user is in wrong state'),
        'user_unblock':              _('Error: unlocking user failed.'),
        'user_unset_admin':          _('Error: unsetting admin failed.'),

    #===============================================================================
    # CM ERRORS
    #===============================================================================
        'cm_error':                  _('Server error.'),

        'admin_add':                 _('Error: setting admin failed.'),

        'ctx_error':                 _('Error in contextualization module.'),
        'ctx_timeout':               _('Error: connecting to contextualization failed.'),
        'ctx_execute_command':       _('Error: executing command failed.'),

        'farm_create':               _('Error: creating farm failed.'),
        'farm_destroy':              _('Error: destroying farm failed.'),
        'farm_wrong_state':          _('Error: wrong farm state.'),

        'image_attached':            _('Error: image already attached.'),
        'image_calculate_size':      _('Error: calculating size of image failed.'),
        'image_change_type':         _('Error: changing type failed.'),
        'image_create':              _('Error: creating image failed.'),
        'image_delete':              _('Error: deleting image failed.'),
        'image_edit':                _('Error: editing image failed.'),
        'image_get':                 _('Error: image not found.'),
        'image_not_found':           _('Error: image not found.'),
        'image_permission':          _('Error: you have no permissions.'),
        'image_set_group':           _('Error: attaching image to group failed.'),
        'image_set_private':         _('Error: setting image to private failed.'),
        'image_set_public':          _('Error: setting image to public failed.'),
        'image_unavailable':         _('Error: image is not available.'),

        'lease_create':              _('Error: creating node failed.'),
        'lease_attached':            _('Error: Lease is attached to vm.'),

        'node_create':               _('Error: creating node failed.'),
        'node_delete':               _('Error: deleting node failed.'),
        'node_edit':                 _('Error: editing node failed.'),
        'node_get':                  _('Error: not enough resources. Choose smaller template or try again later.'),
        'node_has_vms':              _('Error: node has running virtual machines.'),
        'node_lock':                 _('Error: locking node failed.'),
        'node_unlock':               _('Error: unlocking node failed.'),

        'public_lease_assign':       _('Error: assigning public IP address failed.'),
        'public_lease_limit':        _('Error: IP limit reached.'),
        'public_lease_request':      _('Error: requesting IP address failed.'),
        'public_lease_unassign':     _('Error: revoking IP address failed.'),

        'storage_already_exist':     _('Error: storage with this name and mountpoint already exist.'),
        'storage_image_attach':      _('Error: attaching disk failed.'),
        'storage_image_detach':      _('Error: detaching disk failed.'),

        'template_create':           _('Error: creating template failed.'),
        'template_delete':           _('Error: deleting template failed.'),
        'template_edit':             _('Error: editing template failed.'),
        'template_get':              _('Error: template not found.'),

        'user_change_quota':         _('Error: changing quota failed.'),
        'user_cpu_limit':            _('Error: CPU limit reached.'),
        'user_create':               _('Error: creating user failed.'),
        'user_memory_limit':         _('Error: memory limit reached.'),
        'user_points_limit':         _('Error: points limit reached.'),
        'user_storage_limit':        _('Error: user quota exceeded.'),

        'vm_already_closing':        _('Error: virtual machine is already closing.'),
        'vm_cannot_shutdown':        _('Error: shutting down virtual machine failed. Please shutdown your machine from the machine\'s operating system.'),
        'vm_create':                 _('Error: creating virtual machine failed.'),
        'vm_ctx_connect':            _('Error: connecting to contextualization failed.'),
        'vm_destroy':                _('Error: destroying virtual machine failed.'),
        'vm_get':                    _('Error: virtual machine not found.'),
        'vm_get_lv_domain':          _('System error.'),
        'vm_hasnt_lease':            _('Error: virtual machine does not have an IP address assigned.'),
        'vm_has_public_lease':       _('Error: virtual machine already has an IP address assigned.'),
        'vm_restart':                _('Error: resetting virtual machine failed.'),
        'vm_save':                   _('Error: saving virtual machine failed.'),
        'vm_wrong_state':            _('Error: wrong virtual machine state.'),
        'vm_vnc_attached':           _('Error: VNC already attached.'),

        'vnc_attach':                _('Error: VNC failed.'),

        'network_delete':            _('Error: Cannot delete network.'),
        'network_in_use':            _('Error: Network is still in use.'),
        'network_not_available':     _('Error: No network is available at this moment.'),
        'network_type':              _('Error: Unsupported network type. Contact Administrator.'),
    }
    return force_escape(errors.get(error_key) or error_key)


def get_message(message_key, params):
    """
    Method returns error message containing given parameters.
    """
    from django.core.urlresolvers import reverse

    # # message_codes - dictionary of the error <b>messages' keys</b> and <b>messages</b>
    #  (for error messages with parameters).

    message_codes = {'farm_create':        _('Error: starting farm: <em>%(name)s</em> (ID: %(id)s) failed.'),
                     'vm_create':          _('Error: starting virtual machine: <em>%(name)s</em> (ID: %(id)s) failed.'),
                     'vm_save':            _('Error: saving virtual machine: <em>%(name)s</em> (ID: %(id)s) failed.'),
                     'vm_destroy':         _('Error: destroying virtual machine: <em>%(name)s</em> (ID: %(id)s) failed.'),
                     'image_init':         _('Error: creating image: <em>%(name)s</em> (ID: %(id)d) failed.'),
                     'image_create':       _('Error: creating image: <em>%(name)s</em> (ID: %(id)d, size: %(size)d MB) failed.'),
                     'image_download':     _('Error: downloading image: <em>%(name)s</em> (ID: %(id)d) from %(path)s failed.'),
                     'image_format':       _('Error: formating image: <em>%(name)s</em> (ID: %(id)d) with filesystem %(filesystem)s failed.'),
                     'group_request':      _('<em>%(first_name)s %(last_name)s</em> wants to join to group <a href="%(grp_details_url)s"> <b>%(group_name)s</b></a>.'),
                     'image_created':      _('Image <em>%(name)s</em> created.'),
                     'image_downloaded':   _('Image <em>%(name)s</em> downloaded (md5sum: <em>%(md5sum)s</em>).'),
                     'point_limit':        _('Point limit reached: %(used_points)d / %(point_limit)d.'),
                     'vm_saved':           _('VM %(vm_name)s saved successfuly. You can find it on the list of private images.'),
                     'farm_saved':         _('Farm %(farm_name)s saved successfuly. You can find it on the list of private images.'),
                     }
    if message_codes.get(message_key) is None:
        return message_key
    message = _('Bad message code.')
    params = dict((k, force_escape(v) if isinstance(v, str) else v) for k, v in params.iteritems())
    if message_key == 'group_request':
        params['grp_details_url'] = reverse('grp_details', args=[params['group_id']])
    try:
        message = message_codes.get(message_key) % params
    except Exception:
        wi_logger = logging.getLogger('wi_logger')
        wi_logger.error('get_message( message_key=%s, params=%s)' % (message_key, params))
    return message
