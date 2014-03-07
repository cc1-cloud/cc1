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

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'cm_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('memory', self.gf('django.db.models.fields.IntegerField')()),
            ('cpu', self.gf('django.db.models.fields.IntegerField')()),
            ('storage', self.gf('django.db.models.fields.IntegerField')()),
            ('public_ip', self.gf('django.db.models.fields.IntegerField')()),
            ('points', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('cm', ['User'])

        # Adding model 'Admin'
        db.create_table(u'cm_admin', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cm.User'], unique=True, primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('cm', ['Admin'])

        # Adding model 'Lease'
        db.create_table(u'cm_lease', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('user_network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.UserNetwork'])),
            ('vm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.VM'], null=True, blank=True)),
        ))
        db.send_create_signal('cm', ['Lease'])

        # Adding model 'UserNetwork'
        db.create_table(u'cm_usernetwork', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('mask', self.gf('django.db.models.fields.IntegerField')()),
            ('available_network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.AvailableNetwork'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('cm', ['UserNetwork'])

        # Adding model 'AvailableNetwork'
        db.create_table(u'cm_availablenetwork', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('mask', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('cm', ['AvailableNetwork'])

        # Adding model 'Node'
        db.create_table(u'cm_node', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('transport', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('driver', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('cpu_total', self.gf('django.db.models.fields.IntegerField')()),
            ('memory_total', self.gf('django.db.models.fields.IntegerField')()),
            ('hdd_total', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('cm', ['Node'])

        # Adding model 'PublicIP'
        db.create_table(u'cm_publicip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('lease', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.Lease'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='public_ips', null=True, to=orm['cm.User'])),
        ))
        db.send_create_signal('cm', ['PublicIP'])

        # Adding model 'Template'
        db.create_table(u'cm_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('memory', self.gf('django.db.models.fields.IntegerField')()),
            ('cpu', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('points', self.gf('django.db.models.fields.IntegerField')()),
            ('ec2name', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('cm', ['Template'])

        # Adding model 'Farm'
        db.create_table(u'cm_farm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('head', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['cm.VM'])),
        ))
        db.send_create_signal('cm', ['Farm'])

        # Adding model 'Storage'
        db.create_table(u'cm_storage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('capacity', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('dir', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
            ('transport', self.gf('django.db.models.fields.CharField')(default='netfs', max_length=20)),
        ))
        db.send_create_signal('cm', ['Storage'])

        # Adding model 'Image'
        db.create_table(u'cm_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.User'])),
            ('disk_dev', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('disk_controller', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('storage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.Storage'], null=True, blank=True)),
            ('progress', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('access', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('platform', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('network_device', self.gf('django.db.models.fields.IntegerField')(default=1, null=True)),
            ('video_device', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('vm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.VM'], null=True, blank=True)),
        ))
        db.send_create_signal('cm', ['Image'])

        # Adding model 'VM'
        db.create_table(u'cm_vm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.Node'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.User'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.Template'])),
            ('system_image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.Image'])),
            ('iso_image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.Image'], null=True, blank=True)),
            ('libvirt_id', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('stop_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ctx_key', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ctx_api_version', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('vnc_passwd', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('ssh_key', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ssh_username', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('save_vm', self.gf('django.db.models.fields.IntegerField')()),
            ('farm', self.gf('django.db.models.fields.related.ForeignKey')(related_name='vms', null=True, to=orm['cm.Farm'])),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('vnc_port', self.gf('django.db.models.fields.IntegerField')()),
            ('vnc_enabled', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('reservation_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('user_data', self.gf('django.db.models.fields.CharField')(max_length=32768, null=True, blank=True)),
        ))
        db.send_create_signal('cm', ['VM'])

        # Adding model 'Command'
        db.create_table(u'cm_command', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('args', self.gf('django.db.models.fields.CharField')(max_length=100000)),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('response', self.gf('django.db.models.fields.CharField')(max_length=100000, null=True)),
            ('vm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.VM'])),
        ))
        db.send_create_signal('cm', ['Command'])

        # Adding model 'SystemImageGroup'
        db.create_table(u'cm_systemimagegroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group_id', self.gf('django.db.models.fields.IntegerField')()),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cm.Image'])),
        ))
        db.send_create_signal('cm', ['SystemImageGroup'])

        # Adding unique constraint on 'SystemImageGroup', fields ['group_id', 'image']
        db.create_unique(u'cm_systemimagegroup', ['group_id', 'image_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SystemImageGroup', fields ['group_id', 'image']
        db.delete_unique(u'cm_systemimagegroup', ['group_id', 'image_id'])

        # Deleting model 'User'
        db.delete_table(u'cm_user')

        # Deleting model 'Admin'
        db.delete_table(u'cm_admin')

        # Deleting model 'Lease'
        db.delete_table(u'cm_lease')

        # Deleting model 'UserNetwork'
        db.delete_table(u'cm_usernetwork')

        # Deleting model 'AvailableNetwork'
        db.delete_table(u'cm_availablenetwork')

        # Deleting model 'Node'
        db.delete_table(u'cm_node')

        # Deleting model 'PublicIP'
        db.delete_table(u'cm_publicip')

        # Deleting model 'Template'
        db.delete_table(u'cm_template')

        # Deleting model 'Farm'
        db.delete_table(u'cm_farm')

        # Deleting model 'Storage'
        db.delete_table(u'cm_storage')

        # Deleting model 'Image'
        db.delete_table(u'cm_image')

        # Deleting model 'VM'
        db.delete_table(u'cm_vm')

        # Deleting model 'Command'
        db.delete_table(u'cm_command')

        # Deleting model 'SystemImageGroup'
        db.delete_table(u'cm_systemimagegroup')


    models = {
        'cm.admin': {
            'Meta': {'object_name': 'Admin'},
            'password': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cm.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cm.availablenetwork': {
            'Meta': {'object_name': 'AvailableNetwork'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mask': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {})
        },
        'cm.command': {
            'Meta': {'object_name': 'Command'},
            'args': ('django.db.models.fields.CharField', [], {'max_length': '100000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '100000', 'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'vm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.VM']"})
        },
        'cm.farm': {
            'Meta': {'object_name': 'Farm'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'head': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['cm.VM']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.User']"})
        },
        'cm.image': {
            'Meta': {'object_name': 'Image'},
            'access': ('django.db.models.fields.SmallIntegerField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'disk_controller': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'disk_dev': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'network_device': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True'}),
            'platform': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'progress': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.SmallIntegerField', [], {}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.Storage']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.User']"}),
            'video_device': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'vm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.VM']", 'null': 'True', 'blank': 'True'})
        },
        'cm.lease': {
            'Meta': {'object_name': 'Lease'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.UserNetwork']"}),
            'vm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.VM']", 'null': 'True', 'blank': 'True'})
        },
        'cm.node': {
            'Meta': {'object_name': 'Node'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cpu_total': ('django.db.models.fields.IntegerField', [], {}),
            'driver': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'hdd_total': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memory_total': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'transport': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'cm.publicip': {
            'Meta': {'object_name': 'PublicIP'},
            'address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lease': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.Lease']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'public_ips'", 'null': 'True', 'to': "orm['cm.User']"})
        },
        'cm.storage': {
            'Meta': {'object_name': 'Storage'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'capacity': ('django.db.models.fields.IntegerField', [], {}),
            'dir': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'transport': ('django.db.models.fields.CharField', [], {'default': "'netfs'", 'max_length': '20'})
        },
        'cm.systemimagegroup': {
            'Meta': {'unique_together': "(('group_id', 'image'),)", 'object_name': 'SystemImageGroup'},
            'group_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.Image']"})
        },
        'cm.template': {
            'Meta': {'object_name': 'Template'},
            'cpu': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'ec2name': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memory': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {})
        },
        'cm.user': {
            'Meta': {'object_name': 'User'},
            'cpu': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memory': ('django.db.models.fields.IntegerField', [], {}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'public_ip': ('django.db.models.fields.IntegerField', [], {}),
            'storage': ('django.db.models.fields.IntegerField', [], {})
        },
        'cm.usernetwork': {
            'Meta': {'object_name': 'UserNetwork'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'available_network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.AvailableNetwork']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mask': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.User']"})
        },
        'cm.vm': {
            'Meta': {'object_name': 'VM'},
            'ctx_api_version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'ctx_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'farm': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vms'", 'null': 'True', 'to': "orm['cm.Farm']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.Image']", 'null': 'True', 'blank': 'True'}),
            'libvirt_id': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.Node']"}),
            'reservation_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'save_vm': ('django.db.models.fields.IntegerField', [], {}),
            'ssh_key': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ssh_username': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'stop_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'system_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.Image']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.Template']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm.User']"}),
            'user_data': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True', 'blank': 'True'}),
            'vnc_enabled': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vnc_passwd': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'vnc_port': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['cm']