#!/usr/bin/env python
#Basic client for the pomodoroTasks2 daemon

import getopt
import dbus
import sys
import os
import re

def usage():
    print """
Usage:"""+ os.path.basename(sys.argv[0])+""" OPTIONS

Daemon options:
   do_start UUID   start the task with the given task
   start           start the last task
   pause           pause the last task
   stop            stop the current task
   reset           reset the numbers of breaks and time left
   status          show the current status of the daemon

Systray options:
   systray         show the change task form

General options:
   -h, --help      show this help
   quit            quit the pomodoro daemon & systray
"""

try:
    opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
except getopt.GetoptError:
    usage()
    sys.exit(1)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage()
        sys.exit(1)
    else:
        usage()
        sys.exit(1)

if len(sys.argv) == 1:
    print "must pass and option. try "+os.path.basename(sys.argv[0])+" -h"
    sys.exit(1)

com=sys.argv[1]

#Get address bus
if os.getenv('DBUS_SESSION_BUS_ADDRESS'):
    dbus_path=str(os.getenv('DBUS_SESSION_BUS_ADDRESS'))
elif os.path.exists("/run/user/"+str(os.getuid())+"/bus"):
    dbus_path="unix:path=/run/user/"+str(os.getuid())+"/bus"

else:
    # We need to get the dbus environment variable 
    # These environment variables are stored in $HOME/.dbus/session-bus
    # there may be old sessions stored in .dbus/session-bus, we need to determine
    # which session to use

    env = os.environ.copy()
    # Fetch all sessions in $HOME/.dbus/session-bus
    dbus_dir=os.path.join(env['HOME'],'.dbus/session-bus')
    dbus_sessions=[]
    for filename in os.listdir(dbus_dir):
        filepath = os.path.join(dbus_dir,filename)
        session=dict()
        with open(filepath, 'r') as f:
            for line in f.readlines():
                if re.match('^#',line):
                    continue
                var,value=line.strip().split('=',1)
                session[var]=value
        dbus_sessions.append(session)

    # Determine which dbus session to use
    # Check pid to see if it is alive
    # If pid is alive see if the name contains dbus-daemon
    for s in dbus_sessions:
        pid=s['DBUS_SESSION_BUS_PID']

        if os.path.exists('/proc/{0}'.format(pid)):
            with open('/proc/{0}/cmdline'.format(pid)) as f:
                cmdline = f.readline().strip()
        else:
            # DBUS process must be dead
            continue

        if re.search('dbus-daemon',cmdline):
            dbus_path=s['DBUS_SESSION_BUS_ADDRESS']
            break

if not dbus_path:
    print "Couldn't find a dbus session address"
    sys.exit(1)

try:
    # use busConnection better than bus = dbus.SessionBus() to work with systemd for example
    bus = dbus.bus.BusConnection(dbus_path)
    session_bus = bus.get_object('org.liloman.pomodoro', "/daemon")
    interface = dbus.Interface(session_bus, "org.liloman.pomodoroInterface")
except:
    print "no pomodoro daemon detected"
    sys.exit(1)

if com == "quit":
    #close systray as well
    interface.do_quit(True)
    print "pomodoro daemon halted"
elif com == "systray":
    # use busConnection better than bus = dbus.SessionBus() to work with systemd for example
    bus = dbus.bus.BusConnection(dbus_path)
    session_bus = bus.get_object('org.liloman.pomodoro.systray', "/systray")
    systray = dbus.Interface(session_bus, "org.liloman.pomodoro.systrayInterface")
    systray.show_change_task()
elif com == "do_start":
    if len(sys.argv) != 3:
        print "must pass a valid uuid"
        sys.exit(1)
    dic = dbus.Dictionary({'uuid': sys.argv[2] , 'resume': 'No'  } , signature = 'ss' )
    print ("reply:"+interface.do_start(dic)[0])
else:
    print(u''.join(interface.do_fsm(com)[0]).encode('utf-8').strip())

