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
from datetime import datetime
from django.core.management.base import BaseCommand
import sys
import traceback
from django.conf import settings
from django.db import connections
from django.db import transaction
from optparse import make_option


tables = {
    'admin': {
        'name': 'cm_admin',
        'rename_columns': {
            'id': 'user_id'
        }
    },
    'command': {
        'name': 'cm_command',
        'drop_column': ['kwargs']
    },
    'farm': {
        'name': 'cm_farm',
        'drop_column': ['public_key']
    },
    'user': {
        'name': 'cm_user'
    },
    'vm': {
        'name': 'cm_vm',
        'rename_columns': {
            'save': 'save_vm',
            'image_id': 'system_image_id'
        },
    },
    'node': {
        'name': 'cm_node',
        'drop_column': ['interface']
    },
    'template': {
        'name': 'cm_template',
    },
    'storage': {
        'name': 'cm_storage',
    },
    'image_group': {
        'name': 'cm_systemimagegroup',
    }
}

MCURSOR = None
PCURSOR = None


def mselect(query):
    # print "MYSQL: %s" % query
    MCURSOR.execute(query)
    return MCURSOR.fetchall()


def pinsert(query):
    # print "POSTGRESQL: %s" % query
    PCURSOR.execute(query)


def prepare(row):
    nrow = []
    for i in row:
        if i is None:
            nrow.append('NULL')
        elif type(i) == long:
            nrow.append("%d" % i)
        else:
            nrow.append("E'%s'" % str(i).replace("'", "\\'"))
    return ','.join(nrow)


class Command(BaseCommand):
    args = ''
    help = 'Run migration from version 1.7'
    option_list = BaseCommand.option_list + (
        make_option('--name',
                    action='store',
                    dest='name',
                    default='cm',
                    help='MySQL database name'),
        make_option('--password',
                    action='store',
                    dest='password',
                    default='cc1',
                    help='MySQL database password'),
        make_option('--user',
                    action='store',
                    dest='user',
                    default='cc1',
                    help='MySQL database user'),
        make_option('--host',
                    action='store',
                    dest='host',
                    default='127.0.0.1',
                    help='MySQL database host'),
        make_option('--port',
                    action='store',
                    dest='port',
                    default='3306',
                    help='MySQL database port'),
    )

    def handle(self, *args, **options):
        sys.stdout.write('Run migration at: %s\n' % datetime.now())

        settings.DATABASES.update({
            'mysql': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': options['name'],
                'USER': options['user'],
                'PASSWORD': options['password'],
                'HOST': options['host'],
                'PORT': options['port'],
            }
        })
        try:
            global MCURSOR
            MCURSOR = connections['mysql'].cursor()
        except Exception, e:
            print 'Cannot connect to MySQL database: %s' % e
            sys.exit(1)

        try:
            global PCURSOR
            PCURSOR = connections['default'].cursor()
        except Exception, e:
            print 'Cannot connect to PostgresSQL database: %s' % e
            sys.exit(1)

        with transaction.commit_manually():
            try:
                # migrate table from dictionary
                for table, desc in tables.iteritems():
                    print 'Migrate table %s' % table
                    new_table = desc.get('name') or 'cm_%s' % table
                    old_cols = [i[0] for i in mselect("describe %s;" % table)]
                    for name in desc.get('drop_column', []):
                        old_cols.remove(name)
                    new_cols = old_cols[:]
                    rename_columns = desc.get('rename_columns')
                    if rename_columns:
                        for i, c in enumerate(old_cols):
                            if c in rename_columns:
                                new_cols[i] = rename_columns[c]

                    values = mselect("select %s from %s;" % (','.join(old_cols), table))

                    for row in values:
                        pinsert("insert into %s(%s) values (%s);" % (new_table, ','.join(new_cols), prepare(row)))

                # STORAGE IMAGES - 1
                values = mselect("select id,name,description,user_id,type,disk_dev,creation_date,platform,size,access,"
                                 "state,vm_id,storage_id,network_device,video_device,disk_controller,progress "
                                 "from image;")
                for row in values:
                    row = list(row)
                    row[5] = ord(row[5][2]) - 96 # changing sda to 1,  sdb to 2 and so on
                    pinsert("insert into cm_image (id,name,description,user_id,type,disk_dev,creation_date,"
                            "platform,size,access,state,vm_id,storage_id,network_device,video_device,"
                            "disk_controller,progress) values(%s);" % prepare(row))

                # PUBLIC IP
                values = mselect("select id, ip, user_id from public_lease;")
                for row in values:
                    pinsert("insert into cm_publicip (id, address, user_id) values(%s);" % prepare(row))

                transaction.commit()
            except:
                traceback.print_exc()

                transaction.rollback()
            print "Migration complete"

