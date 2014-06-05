import sys
import os
import libvirt
import commands

sys.path.append('/usr/lib/cc1/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cm.settings")
from cm.models.vm import VM
from cm.models.node import Node
from cm.models.lease import Lease
from cm.models.public_ip import PublicIP
from common.states import vm_states

vm_states_reversed = dict((v, k) for k, v in vm_states.iteritems())


cmds = {
    'n_images': 'ls /images',
    'n_nets': '/sbin/ifconfig | awk "/br-[0-9]+-[0-9]+/ {print \$1}"',
    'n_bridge': '/sbin/brctl show | awk "/br-[0-9]+-[0-9]+/ {print \$1}"',
    'n_public_ip': '/sbin/ifconfig | awk "/eth2:[0-9]+/ {eth=\$1; getline; ad=\$2; sub(\\"eth2:\\", \\"\\", eth); sub(\\"addr:\\", \\"\\", ad); print eth \\":\\" ad}"',
    'n_nets_ip': '/sbin/ifconfig | awk "/br-[0-9]+-[0-9]+/ {br=\$1; getline; ad=\$2; sub(\\"addr:\\", \\"\\", ad); print br \\":\\" ad}"',
}


def ssh_exec(addr, cmd):
    retr = commands.getoutput('ssh %s \'%s\' 2>/dev/null' % (addr, cmd)).split()
    return retr


def check_vms(lv_vms, db_vms):
    vms = {'vm-%d-%d' % (vm['id'], vm['user_id']): vm['state'] for vm in db_vms}
    for vm in lv_vms:
        try:
            vm_state = vm_states_reversed[vms[vm]]
            if vm_state != 'running' and vm_state != 'running ctx':
                print 'vm: ', vm, vm_state
        except KeyError, e:
            print 'vm: ', vm, 'not in db'
        except Exception, e:
            print 'vm: ', vm, 'other err: %s' % e


def check_images(db_vms, n_images):
    vms = {vm['id']: vm['state'] for vm in db_vms}
    for image in n_images:
        try:
            vm_state = vm_states_reversed[vms[int(image)]]
            if vm_state != 'running' and vm_state != 'running ctx':
                print 'image: ', image, vm_state
        except KeyError, e:
            print 'image: ', image, 'not in db'
        except ValueError, e:
            print 'image: ', image, 'strange name'
        except Exception, e:
            print 'image: ', image, 'other err: %s' % e


def print_diffs(db_vms, params):
    vms = { vm['id']: '%s' % (vm_states_reversed[vm['state']]) for vm in db_vms }
    for par in params:
        if params[par]:
            for p in params[par]:
                try:
                    vm_info = '%s' % vms[int(p)]
                except Exception, e:
                    vm_info = ''
                print par, p, vm_info


def check_vms_2(lv_vms, db_vms, n_images):
    db_vms = ['vm-%d-%d' % (vm['id'], vm['user_id']) for vm in db_vms if vm_states_reversed[vm['state']] == 'running' or vm_states_reversed[vm['state']] == 'running ctx']
    common_vms = set(db_vms) & set(lv_vms)

    db_vms_c = set(db_vms) - common_vms
    lv_vms_c = set(lv_vms) - common_vms

    db_vms_ci = [db.split('-')[1] for db in db_vms]
    lv_vms_ci = [db.split('-')[1] for db in lv_vms]
    common_images = set(db_vms_ci) & set(lv_vms_ci) & set(n_images)

    n_images_c = set(n_images) - common_images

    return {'VM in DB:': db_vms_c, 'VM in libvirt:': lv_vms_c, 'image on HD:': n_images_c}


def check_networks(n_nets, n_bridge, n_public_ip, lv_nets, db_nets, db_public_ip):
    n_nets_c = [a.replace('br-', '') for a in n_nets]
    n_bridge_c = [a.replace('br-', '') for a in n_bridge]
    lv_nets_c = [a.replace('net-', '') for a in lv_nets]
    db_nets_c = ['%d-%d' % (db['vm'], db['lease_id'])  for db in db_nets if db['vm']]
    common_net = set(n_nets_c) & set(n_bridge_c) & set(lv_nets_c) & set(db_nets_c)

    n_nets_c = [n.split('-')[0] for n in (set(n_nets_c) - common_net)]
    n_bridge_c = [n.split('-')[0] for n in (set(n_bridge_c) - common_net)]
    lv_nets_c = [n.split('-')[0] for n in (set(lv_nets_c) - common_net)]
    db_nets_c = [n.split('-')[0] for n in (set(db_nets_c) - common_net)]

    return {'ifconfig net:': n_nets_c, 'brctl net:': n_bridge_c, 'libvirt net:': lv_nets_c, 'DB net:': db_nets_c}


print 'getting all vms'
db_all_vms = [{'id': vm.id, 'user_id': vm.user_id, 'state': vm.state, 'vnc_port': vm.vnc_port, 'node': vm.node.ssh_string} for vm in VM.objects.all()]
for node in [{'id': n.id, 'addr':n.ssh_string} for n in Node.objects.filter(state=1).all()]:
    print '-'*80
    print node['addr']
    #['202', '203', '204', '206']
    #['img_id']
    n_images = ssh_exec(node['addr'], cmds['n_images'])
    n_images.remove('lost+found')
    n_images.remove('info')

    #['br-236-74:10.16.64.225', 'br-237-71:10.16.64.213']
    #['interface:ip_addr']
    n_nets = ssh_exec(node['addr'], cmds['n_nets'])

    #['br-236-74', 'br-237-71']
    #['interface']
    n_bridge = ssh_exec(node['addr'], cmds['n_bridge'])

    #['15804:192.245.169.39', '16771:192.245.169.88']
    #['vm_id:ip_addr']
    n_public_ip = ssh_exec(node['addr'], cmds['n_public_ip'])

    lv_c=libvirt.open('qemu+ssh://%s/system' % (node['addr']))
    #['vm-239-1', 'vm-243-1', 'vm-240-1']
    #['vm_name']
    lv_vms = [lv_c.lookupByID(x).name() for x in lv_c.listDomainsID()]

    #['net-236-74', 'net-237-71', 'net-238-72']
    #['net_name']
    lv_nets = lv_c.listNetworks()

    #[{'id': 28, 'state': 3, 'user_id': 2, 'vnc_port': 5907}, {'id': 32, 'state': 3, 'user_id': 2, 'vnc_port': 5907}]
    db_vms = [{'id': vm.id, 'user_id': vm.user_id, 'state': vm.state, 'vnc_port': vm.vnc_port} for vm in VM.objects.filter(node_id=node['id']).all()]

    #{'address': '10.16.64.26', 'lease_id': 6, 'public_ip': '', 'user_id': 1, 'user_network_id': 1, 'vm': None}
    db_nets = [lease.dict for lease in Lease.objects.filter(vm__node_id=node['id']).all()]

    #[{'lease': None, 'public_addr': '192.168.1.7'}, {'lease': None, 'public_addr': '192.245.169.63'}]
    db_public_ip = [{'lease': pub.lease, 'public_addr': pub.address} for pub in PublicIP.objects.all()]

    retr = check_vms_2(lv_vms, db_vms, n_images)
    print_diffs(db_all_vms, retr)

    retr = check_networks(n_nets, n_bridge, n_public_ip, lv_nets, db_nets, db_public_ip)
    print_diffs(db_all_vms, retr)

#dnsmasq:
#ps aux | awk "/[d]nsmasq/ {net = match(\$0, \"net-[0-9]+-[0-9]+\"); n=substr(\$0, net); print n}"
