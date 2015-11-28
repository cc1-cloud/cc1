# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @COPYRIGHT_end

import os
import subprocess
import random
import string
import pwd
import grp

VERSION = 3

"""@package src.cm.views.ctx.actions

@defgroup CTX VM Exceptions
@{
"""


def missing_parameter(param):
    """
    Method to raise Exception for missing parameter.
    @param_post{param} missing parameter
    """
    raise Exception("The request must contain the parameter %s" % param)


def execution_error(error):
    """
    Method to raise Exception for execution error.
    @param_post{error} execution's error
    """
    raise Exception("There was problem during function execution: %s" % error)


def build_in_command_failed(cmd, code):
    """
    Method to raise Exception for build in command's failure.
    @param_post{cmd}
    @param_post{code}
    """
    raise Exception("Build in command %s failed with exit code: %s" % (cmd, code))


def update_hosts(hosts_list=None, user='root'):
    """
    @param_post{hosts_list}
    @param_post{user} (optional, default: @val{root})
    """
    if user is None:
        missing_parameter('user')
    if hosts_list is None:
        missing_parameter('host_list')
    try:
        f = open("/etc/hosts", "r")
        lines = f.readlines()
        f.close()
    except IOError, e:
        execution_error(e.strerror)
    lines[:] = [line for line in lines if not line.find("farm") != -1]

    known_hosts = open(os.path.expanduser('~%s/.ssh/known_hosts' % user), "a")

    for host in hosts_list:
        lines.append("%s\t%s\n" % (host["ip"], host["host_name"]))

    try:
        f = open("/etc/hosts", 'w')
        f.writelines(lines)
        f.close()
    except IOError, e:
        execution_error(e.strerror)
    return (True, 'ok')

    for host in hosts_list:
        r = subprocess.call(['ssh-keyscan', host["ip"]], stdout=known_hosts)
        if r != 0:
            build_in_command_failed("ssh-keyscan", r)
        r = subprocess.call(['ssh-keyscan', host["host_name"]], stdout=known_hosts)
        if r != 0:
            build_in_command_failed("ssh-keyscan", r)


def set_hostname(hostname=None):
    """
    @param_post{hostname}
    """
    if hostname == None:
        missing_parameter('hostname')
    r = subprocess.call(['hostname', hostname])
    if r != 0:
        build_in_command_failed('hostname', r)


def cmd_exists(cmd):
    """
    @param_post{cmd}
    """
    return subprocess.call(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def shutdown():
    """
    Tries to shutdown VM. If fails, raises exception.
    """
    r = 'not working cmd'
    if cmd_exists('poweroff'):
        r = subprocess.call('sleep 5 && poweroff &', shell=True)
    elif cmd_exists('shutdown'):
        r = subprocess.call('sleep 5 && shutdown -h now', shell=True)
    if r != 0:
        build_in_command_failed('shutdown', r)


def reboot():
    """
    Tries to restart VM. If fails, raises exception.
    """
    r = 'not working cmd'
    if cmd_exists('reboot'):
        r = subprocess.call(['reboot'])
    elif cmd_exists('shutdown'):
        r = subprocess.call(['shutdown', '-r', 'now'])
    if r != 0:
        build_in_command_failed('shutdown', r)


def reset_password(user=None):
    """
    Tries to reset password of ther user
    @param_post{user}
    """
    if user == None:
        build_in_command_failed('user')
    chars = string.ascii_letters + string.digits

    random.seed = (os.urandom(1024))
    password = ''.join(random.choice(chars) for unused in range(12))
    p = subprocess.Popen(('openssl', 'passwd', '-1', password), stdout=subprocess.PIPE)
    shadow_password = p.communicate()[0].strip()

    if p.returncode != 0:
        build_in_command_failed('openssl', p.returncode)

    p = subprocess.Popen(['chpasswd', '-e'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate('%s:%s\n' % (user, shadow_password))
    if r[1]:
        build_in_command_failed('chpasswd', r[1])
    if p.returncode != 0:
        build_in_command_failed('chpasswd', p.returncode)
    return password


def add_ssh_key(user=None, ssh_key=None):
    """
    @param_post{user}
    @param_post{ssh_key}
    """
    if user is None:
        missing_parameter('user')
    if ssh_key is None:
        missing_parameter('ssh_key')

    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        keys_path = os.path.expanduser('~%s/.ssh/authorized_keys' % user)
        if not os.path.exists(keys_path):
            d = os.path.dirname(os.path.expanduser('~%s/.ssh/' % user))
            if not os.path.exists(d):
                os.makedirs(d)
            os.chown(d, uid, gid)
            fp = file(keys_path, 'w')
            fp.close()

        fp = file(keys_path, 'a')
        fp.write('\n%s\n' % ssh_key)
        fp.close()
        os.chown(keys_path, uid, gid)

        ssh_conf = open("/etc/ssh/ssh_config", 'r')
        lines = ssh_conf.readlines()
        ssh_conf.close()

        lines[:] = [line for line in lines if line.find("StrictHostKeyChecking") == -1]
        lines.append("StrictHostKeyChecking no")
        ssh_conf = open("/etc/ssh/ssh_config", 'w')
        ssh_conf.writelines(lines)
        ssh_conf.close()
    except IOError, e:
        execution_error(e.strerror)


def generate_key(key_name="id_rsa"):
    """
    Creates pair of ssh keys on the machine (public - private)
    and then returns public.
    @param_post{key_name} @optional{"id_rsa"}
    """
    user = 'root'

    key_name = os.path.expanduser('~%s/.ssh/' % user) + key_name
    if not os.path.exists(key_name):
        subprocess.call(["ssh-keygen", "-q", "-N", "", "-f", key_name])

    try:
        f = open("%s.pub" % key_name, "r")
        key = f.read().strip()
        f.close()
    except IOError, e:
        execution_error(e.strerror)
    return key
