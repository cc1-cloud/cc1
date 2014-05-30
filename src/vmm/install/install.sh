#! /bin/bash

VMM_ADDR=http://cc1.ifj.edu.pl/vmm/vmm.tar.gz
TEMP_DIR="cc1-$RANDOM.$RANDOM"

function remove_old_ctx {
	pid=$(ps aux | grep '[V]MMDaemon.py' | awk '{print $2}')
	[ -n "$pid" ] && kill -9 $pid
	[ -f /etc/rc.local ] && sed -i '/VMMDaemon.py/d' /etc/rc.local

	for path in "/opt/vmm" "/opt/cc1/vmm"
	do
		[ -d "$path" ] && rm -rf "$path"
	done
}

function remove_ctx {
	pid=$(ps aux | grep  '[c]c1/vmm/main.py' | awk '{print $2}')
	[ -n "$pid" ] && kill -9 $pid
	[ -f /etc/init.d/cc1-vmm ] && rm /etc/init.d/cc1-vmm

	for path in "/opt/vmm" "/opt/cc1/vmm" "/var/log/cc1/vmm/"
	do
		[ -d "$path" ] && rm -rf "$path"
	done
}


function find_python {
	for py in "python" "python27" "python2.7" "python26" "python2.6"
	do
		if pypath=$(which ${py} 2>/dev/null); then
			#ver=$($pypath -V)
			$pypath -c 'import sys; sys.exit(sys.hexversion<0x02060000)' && echo $pypath && return 0
		fi
	done
	return 1
}

function wget_vmm {
	mkdir -p $TEMP_DIR
	if [ -x /usr/bin/wget ] ; then
        wget $VMM_ADDR -qO $TEMP_DIR/vmm.tar.gz || return 1
    else
        curl $VMM_ADDR -o $TEMP_DIR/vmm.tar.gz || return 1
    fi
    [ -f $TEMP_DIR/vmm.tar.gz ] && tar zxf $TEMP_DIR/vmm.tar.gz -C $TEMP_DIR/ || return 1
}

function prepare_init {
	sed -i "s,PYTHON_BIN=,&${pypath}," $TEMP_DIR/vmm.sh
	cp $TEMP_DIR/vmm.sh /etc/init.d/cc1-vmm
	chmod +x /etc/init.d/cc1-vmm
}

function deb {
	apt-get update
	apt-get -y install python-setuptools
	pypath=$(find_python)
	easy_install requests
	prepare_init
	update-rc.d cc1-vmm defaults
}

function redhat {
	yum -y install python-setuptools python26-distribute
	pypath=$(find_python)
	easy_install-2.6 requests || wget https://bitbucket.org/pypa/setuptools/raw/0.7.4/ez_setup.py -O - | $pypath && easy_install-2.6 requests
	prepare_init
	chkconfig --add cc1-vmm	
}

function clean {
	[ -d $TEMP_DIR ] && rm -rf $TEMP_DIR
}


remove_old_ctx
remove_ctx
wget_vmm || exit 1

mkdir -p /opt/cc1/vmm
mkdir -p /var/log/cc1/vmm/
cp $TEMP_DIR/main.py $TEMP_DIR/settings.py $TEMP_DIR/Input.py $TEMP_DIR/ioctl.py /opt/cc1/vmm/

if [ -x /sbin/chkconfig ] ; then
	#echo 'redhat'
	redhat
elif [ -x /usr/sbin/update-rc.d ] ; then
	#echo 'debian'
	deb
else
	echo 'Distro not supported'
fi

echo "service starting"
service cc1-vmm start
service cc1-vmm status

clean
