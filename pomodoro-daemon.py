#!/usr/bin/env python
# Pomodoro daemon with FSM

import os
import threading
from tasklib import TaskWarrior, Task
# import datetime 
from datetime import datetime

#For GUI 
import subprocess
from gi.repository import GObject
import sys

# For dbus
import dbus.service
import dbus.mainloop.glib

dirname, filename = os.path.split(os.path.realpath(__file__))
#change to the project real dir
os.chdir(dirname)

class Pomodoro(dbus.service.Object):

    #Finite State Machine logic (FSM)
    # [from-event]=to
    events = {
            'started-stop': 'do_stop',
            'started-start': 'do_warning' ,
            'started-pause': 'do_pause' ,
            'started-stop': 'do_stop',
            'started-reset': 'do_reset',
            'started-status': 'do_status',
            'paused-start': 'do_resume',
            'paused-stop': 'do_stop',
            'paused-reset': 'do_reset',
            'paused-pause': 'do_resume',
            'paused-status': 'do_status',
            'stopped-start': 'do_resume',
            'stopped-pause': 'do_resume',
            'stopped-stop': 'do_warning',
            'stopped-reset': 'do_reset',
            'stopped-status': 'do_status',
            'started-take_break': 'do_timeout',
            'started-dry_start': 'do_warning' ,
            'started-dry_stop': 'do_dry_stop',
            'stopped-dry_start': 'do_dry_start',
            'paused-dry_start': 'do_dry_start',
            'stopped-dry_stop': 'do_warning',
            }
    bus_name = "org.liloman.pomodoro"
    state = ""
    #timeout pomodoro (minutes)
    timer_pomodoro = int(os.getenv('POMODORO_TIMEOUT',25))
    #short break time pomodoro (minutes)
    stimeout = str(os.getenv('POMODORO_STIMEOUT',5))
    #long break time pomodoro (minutes)
    ltimeout = str(os.getenv('POMODORO_LTIMEOUT',15))
    #Number of breaks to take a long break (LONG_TIME_BREAK)
    maxbreaks = 4
    #timeout wait for events (seconds)
    timeout = 60
    #Counter for breaks
    breaks = 0
    #Total time elapsed
    time_elapsed = 0
    last_task_id = 0
    tw = None 
    timer = None 
    # default systray icon
    systrayIcon = "images/iconStarted-0.png"

    def __init__(self, rc = '~/.task'):
        self.tw = TaskWarrior(data_location=rc, create=True)
        name = dbus.service.BusName(self.bus_name, bus=dbus.SessionBus(),do_not_queue=True, replace_existing=False, allow_replacement=False )
        dbus.service.Object.__init__(self, name, '/daemon')

    #get active task
    def get_active_task(self):
        for task in self.tw.tasks.pending():
            if task.active:
                #get all fields in task
                task.refresh()
                return task
        return {}

    def update_systray(self):
        try:
            systray_bus = dbus.SessionBus()
            systray_bus = systray_bus.get_object('org.liloman.pomodoro.systray', "/systray")
            interface_systray = dbus.Interface(systray_bus, "org.liloman.pomodoro.systrayInterface")
            status = self.do_status()
            interface_systray.set_state(dbus.Dictionary({'icon': self.systrayIcon, 'state': self.state, 'tooltip': status }, signature='ss'))
        except:
            #print "not systray found"
            return

    def do_pause(self):
        active = self.get_active_task ()
        #if the user mark current as done and dont select a new task to work in
        if active:
            active.stop ()
            self.last_task_id = active['uuid']
        self.state = "paused"
        return "ok"

    #Resume the last task for previous pause/stop
    def do_resume(self):
        #If resumed from pause/stop without changing the current task from GUI
        if  self.last_task_id != 0:
            new=self.tw.tasks.get(uuid=self.last_task_id)
            new.start()
        else: #let just use the timer without any task working in
            self.state = "started"
            return "no previous task"

        #only update time_elapsed when paused
        if  self.state == "stopped":  
            self.time_elapsed = 0 
        self.state = "started"

        return "ok"

    def do_stop(self):
        active = self.get_active_task ()
        if active:
            self.last_task_id = active['uuid']
            active.stop()
        self.state = "stopped"
        self.time_elapsed = 0
        return "ok"

    def do_reset(self):
        self.do_stop()
        self.breaks = 0
        if self.last_task_id != 0:
            self.do_start(dbus.Dictionary({'uuid': self.last_task_id, 'resume': 'No'}))
        else: # if the user wants to reset the timer with no task working in
            self.state = "started"
            return "no previous task"

        return "ok"

    def do_warning(self):
        return "Already "+self.state

    def do_status(self):
        remaining = "%02d:%02d" % divmod(self.timer_pomodoro*60 - self.time_elapsed,60)
        active = self.get_active_task ()
        msg = ""
        if active:
            self.state = "started"
            project=u''.join(active['project']).encode('utf-8').strip() 
            desc=u''.join(active['description']).encode('utf-8').strip() 
            uuid=active['uuid']
            msg="\nBreak num:"+str(self.breaks)+"\nProject:"+project+"\n"+desc
        rest = self.timer_pomodoro / 8
        if rest > 0:
            actual=self.time_elapsed / (rest*60)
        else:
            actual=0
        i_started = "images/iconStarted-{0}.png".format(actual)
        i_no_task = "images/iconStarted-no-task.png"
        i_paused  = "images/iconPaused.png"
        i_stopped = "images/iconStopped.png"
        if self.state == "started" and not active:
            self.systrayIcon=i_no_task 
        elif self.state == "started":
            self.systrayIcon=i_started 
        elif self.state == "paused":
            self.systrayIcon=i_paused
        elif self.state == "stopped":
            self.systrayIcon=i_stopped 

        return self.state+" "+remaining+" left"+msg

    def do_timeout(self):
        self.do_stop()
        self.breaks+=1
        if self.breaks == self.maxbreaks:
            cmd = ['./do_timeout.py', self.ltimeout, str(self.breaks) ]
        else:
            cmd = ['./do_timeout.py', self.stimeout, str(self.breaks) ]
        subprocess.Popen(cmd)
        return "call do_timeout.py"

    def increment(self):
        self.timer = threading.Timer(5.0, self.increment)
        self.timer.start()
        self.update_systray()
        if self.state == "started":
            self.time_elapsed+=5
            if self.time_elapsed >= self.timer_pomodoro*60:
                self.do_timeout()


    @dbus.service.method("org.liloman.pomodoroInterface", in_signature='a{ss}', out_signature='as')
    def do_start(self, dic):
        active = self.get_active_task ()
        prev_state = self.state
        self.state = "started"
        uid=dic['uuid']
        resume=dic['resume']

        #if the user wants to start the timer without any task
        if uid == '0':
            if active:
                #stop current
                active.stop()
                self.last_task_id = 0
            self.update_systray()
            return ["started with no task"]

        #if start a new one when running one already
        if active:
            if active['uuid'] != uid:
                new=self.tw.tasks.get(uuid=uid)
                active.stop()
                new.start()
                if resume == 'No':
                    self.time_elapsed = 0 
                self.update_systray()
                return ["started:"+uid]
            else:
                return ["Already started"]
        else:
            new=self.tw.tasks.get(uuid=uid)
            try:
                new.start()
            except:
                self.state = prev_state
                return ["Incorrect uuid:"+uid+" .The task can't be started"]

            if resume == 'No':
                self.time_elapsed = 0 
            self.update_systray()
            return ["started:"+uid]

   
    @dbus.service.method("org.liloman.pomodoroInterface", in_signature='s', out_signature='as')
    def do_fsm(self, event):
        fsm = "{0}-{1}".format(self.state,event)
        if fsm in self.events:
            fun = getattr(self,self.events[fsm])
            out = fun()
            self.update_systray()
            return [out]
        else:
            return ["event:"+event+" not found"]

    def close_systray(self):
        try:
            systray_bus = dbus.SessionBus()
            systray_bus = systray_bus.get_object('org.liloman.pomodoro.systray', "/systray")
            interface_systray = dbus.Interface(systray_bus, "org.liloman.pomodoro.systrayInterface")
            interface_systray.quit()
        except:
            # print "not systray found"
            return 

    @dbus.service.method("org.liloman.pomodoroInterface", in_signature='', out_signature='as')
    def done_current(self):
        active = self.get_active_task ()
        if not active:
            return ["no active task"]
        active.done()
        return ["ok"]

    @dbus.service.method("org.liloman.pomodoroInterface", in_signature='', out_signature='')
    def quit(self):
        #stop timer
        self.timer.cancel()
        self.close_systray()
        # Exit daemon
        loop.quit()


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = GObject.MainLoop()

    #if testing or with other data.location
    if len(sys.argv) >= 2:
        pomodoro = Pomodoro(sys.argv[1])
    else:
        pomodoro = Pomodoro()
    pomodoro.increment()

    task = pomodoro.get_active_task()
    if task:
        pomodoro.do_start(dbus.Dictionary({'uuid': task['uuid'], 'resume': 'No'}))
    else:
        pomodoro.do_stop()

    #run the systray
    if len(sys.argv) == 2:
            subprocess.Popen(['./pomodoro-systray.py', sys.argv[1]])
    elif len(sys.argv) == 1:
        subprocess.Popen(['./pomodoro-systray.py'])
    #dont lauch the systray when testing len(sys.argv)==3

    loop.run()
