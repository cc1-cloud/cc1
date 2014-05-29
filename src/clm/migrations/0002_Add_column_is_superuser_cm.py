# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'User.is_superuser_cm'
        db.add_column(u'clm_user', 'is_superuser_cm',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'User.is_superuser_cm'
        db.delete_column(u'clm_user', 'is_superuser_cm')


    models = {
        'clm.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {})
        },
        'clm.group': {
            'Meta': {'object_name': 'Group'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_leader_set'", 'to': "orm['clm.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['clm.User']", 'through': "orm['clm.UserGroup']", 'symmetrical': 'False'})
        },
        'clm.key': {
            'Meta': {'object_name': 'Key'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'fingerprint': ('django.db.models.fields.CharField', [], {'max_length': '47'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clm.User']"})
        },
        'clm.message': {
            'Meta': {'object_name': 'Message'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'params': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clm.User']"})
        },
        'clm.news': {
            'Meta': {'object_name': 'News'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sticky': ('django.db.models.fields.IntegerField', [], {}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'clm.user': {
            'Meta': {'object_name': 'User'},
            'act_key': ('django.db.models.fields.CharField', [], {'max_length': '63', 'null': 'True', 'blank': 'True'}),
            'activation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clm.Cluster']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'first': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.IntegerField', [], {}),
            'is_superuser': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'is_superuser_cm': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'last_login_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'login': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '63'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'clm.usergroup': {
            'Meta': {'unique_together': "(('user', 'group'),)", 'object_name': 'UserGroup'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clm.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clm.User']"})
        }
    }

    complete_apps = ['clm']
