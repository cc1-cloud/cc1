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
        # Adding model 'Cluster'
        db.create_table(u'clm_cluster', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('clm', ['Cluster'])

        # Adding model 'User'
        db.create_table(u'clm_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('last', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('default_cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clm.Cluster'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('login', self.gf('django.db.models.fields.CharField')(unique=True, max_length=63)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('act_key', self.gf('django.db.models.fields.CharField')(max_length=63, null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('is_active', self.gf('django.db.models.fields.IntegerField')()),
            ('is_superuser', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('activation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_login_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('clm', ['User'])

        # Adding model 'Key'
        db.create_table(u'clm_key', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clm.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('fingerprint', self.gf('django.db.models.fields.CharField')(max_length=47)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('clm', ['Key'])

        # Adding model 'Message'
        db.create_table(u'clm_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clm.User'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('params', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('clm', ['Message'])

        # Adding model 'News'
        db.create_table(u'clm_news', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('sticky', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('clm', ['News'])

        # Adding model 'Group'
        db.create_table(u'clm_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('leader', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group_leader_set', to=orm['clm.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('clm', ['Group'])

        # Adding model 'UserGroup'
        db.create_table(u'clm_usergroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clm.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clm.Group'])),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('clm', ['UserGroup'])

        # Adding unique constraint on 'UserGroup', fields ['user', 'group']
        db.create_unique(u'clm_usergroup', ['user_id', 'group_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserGroup', fields ['user', 'group']
        db.delete_unique(u'clm_usergroup', ['user_id', 'group_id'])

        # Deleting model 'Cluster'
        db.delete_table(u'clm_cluster')

        # Deleting model 'User'
        db.delete_table(u'clm_user')

        # Deleting model 'Key'
        db.delete_table(u'clm_key')

        # Deleting model 'Message'
        db.delete_table(u'clm_message')

        # Deleting model 'News'
        db.delete_table(u'clm_news')

        # Deleting model 'Group'
        db.delete_table(u'clm_group')

        # Deleting model 'UserGroup'
        db.delete_table(u'clm_usergroup')


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