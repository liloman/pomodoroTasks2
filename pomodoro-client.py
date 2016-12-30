#!/usr/bin/env python
#Basic client for the pomodoroTasks2 daemon

import getopt
import dbus
import sys
import os

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

try:
    bus = dbus.SessionBus()
    session_bus = bus.get_object('org.liloman.pomodoro', "/daemon")
    interface = dbus.Interface(session_bus, "org.liloman.pomodoroInterface")
except:
    print "no pomodoro daemon detected"
    sys.exit(1)

if com == "quit":
    interface.quit()
    print "pomodoro daemon halted"
elif com == "systray":
    bus = dbus.SessionBus()
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
    print (interface.do_fsm(com)[0])

