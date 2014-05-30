# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Node.errors'
        db.add_column(u'cm_node', 'errors',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Node.errors'
        db.delete_column(u'cm_node', 'errors')


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
            'errors': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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