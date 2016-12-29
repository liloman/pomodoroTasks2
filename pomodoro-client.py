#!/usr/bin/env python
#Basic client for the pomodoroTasks2 daemon

import dbus
import sys


if len(sys.argv) == 1:
    print "must pass and option"
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
elif com == "do_start":
    if len(sys.argv) != 3:
        print "must pass a valid uuid"
        sys.exit(1)
    dic = dbus.Dictionary({'uuid': sys.argv[2] , 'resume': 'No'  } , signature = 'ss' )
    print ("reply:"+interface.do_start(dic)[0])
else:
    print (interface.do_fsm(com)[0])

