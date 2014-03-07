#! /bin/sh

# cc1-vmm cc1-vmm init script
#
# chkconfig: 2345 98 24
# description: Virtual Machine Managment Tools for CC1 system


### BEGIN INIT INFO
# Provides:             vmm
# Required-Start:       $remote_fs $syslog
# Required-Stop:        $remote_fs $syslog
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    Virtual Machine Managment Tools for CC1 system
### END INIT INFO


# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="Virtual Machine Managment Tools for CC1 system"
NAME="cc1-vmm"
DAEMON="/opt/cc1/vmm/main.py"
PIDFILE=/var/run/$NAME.pid
LOGFILE=/var/log/cc1/vmm/all
SCRIPTNAME=/etc/init.d/$NAME

PYTHON_BIN=

# Exit if the package is not installed
[ -f "$DAEMON" ] || exit 0


start_vmm()
{
    if [ -f ${PIDFILE} ]; then
        ps=$(ps -p $(cat ${PIDFILE}) -o args=)
        if [ -n "$ps" ]; then
            echo "already running"
            return 1
        else
            rm ${PIDFILE}
        fi
    else 
        pid=$(ps aux | grep  '[c]c1/vmm/main.py' | awk '{print $2}')
        [ -n "$pid" ] && kill -9 $pid
    fi

    echo "starting..."
    $PYTHON_BIN $DAEMON >>$LOGFILE 2>&1 &
    pid=$!
    
    echo "$pid" > ${PIDFILE}
    return 0
}


stop_vmm()
{
    echo "stopping..."
    [ -f ${PIDFILE} ] && kill -9 $(cat ${PIDFILE}) && rm ${PIDFILE} && return 0
    pid=$(ps aux | grep  '[c]c1/vmm/main.py' | awk '{print $2}')
    [ -n "$pid" ] && kill -9 $pid
    return 0
}

status_vmm()
{
    if [ -f ${PIDFILE} ]; then
        ps=$(ps -p $(cat ${PIDFILE}) -o args=)
        [ -n "$ps" ] && echo "VMM is running" && return 0
    fi
    echo "VMM not running"
    return 1
}

case "$1" in
  start)
        start_vmm
        ;;
  stop)
        stop_vmm
        ;;
  status)
        status_vmm
        ;;
  #reload|force-reload)
        #
        # If do_reload() is not implemented then leave this commented out
        # and leave 'force-reload' as an alias for 'restart'.
        #
        #log_daemon_msg "Reloading $DESC" "$NAME"
        #do_reload
        #log_end_msg $?
        #;;
  restart|force-reload)
        #
        # If the "reload" option is implemented then remove the
        # 'force-reload' alias
        #
        stop_vmm
        start_vmm
        ;;
  *)
        #echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
        echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
        exit 3
        ;;
esac




exit 0


