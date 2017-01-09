#!/usr/bin/env python

import subprocess
import dbus
import sys
import os
import gi
gi.require_version('Gtk', '3.0')

from tasklib import TaskWarrior, local_zone
from gi.repository import Gtk, GObject
from datetime import datetime


tw = TaskWarrior()
builder = Gtk.Builder()
builder.add_from_file("gui/timeout.glade")
wTimeout     = builder.get_object("wTimeout")
pbTimeout    = builder.get_object("pbTimeout")
wContinue    = builder.get_object("wContinue")
lsbReminders = builder.get_object("lsbReminders")
bus = dbus.SessionBus()
session_bus = bus.get_object('org.liloman.pomodoro', "/daemon")
interface = dbus.Interface(session_bus, "org.liloman.pomodoroInterface")

###############
#  Reminders  #
###############


def update_reminders():
    i=0
    for task in tw.tasks.filter('+READY +reminder'):
        # for each box 
        for box in lsbReminders.get_row_at_index(i).get_children():
            #get the done checkbox
            if box.get_children()[2].get_active():
                #mark as done the reminder
                task.done()
        i+=1

def addReminder(desc,date):
    row = Gtk.ListBoxRow()
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
    row.add(hbox)
    ldesc = Gtk.Label(desc, xalign=0)
    ldate = Gtk.Label(date, xalign=0)
    cdone = Gtk.CheckButton()
    hbox.pack_start(ldesc, True, True, 0)
    hbox.pack_start(ldate, False, True, 0)
    hbox.pack_start(cdone, False, True, 0)
    lsbReminders.add(row)

#############
#  Events   #
#############

def onYesPressed(self):
    subprocess.Popen(['timew', 'stop'])
    print (interface.do_fsm("start")[0])
    wContinue.destroy()
    Gtk.main_quit()  

def onNoPressed(self):
    subprocess.Popen(['timew', 'stop'])
    wContinue.destroy()
    Gtk.main_quit()  

def onDeleteWindow(self,*args):
    update_reminders()
    wContinue.show_all()

def onBackWorkPressed(self):
    update_reminders()
    subprocess.Popen(['timew', 'stop'])
    print (interface.do_fsm("start")[0])
    Gtk.main_quit()

def do_timeout():
    wTimeout.show_all()

def update_timeout_bar():
    new_value = pbTimeout.get_fraction() + 0.01
    if new_value > 1:
        new_value = 0
        update_reminders()
        wTimeout.destroy()
        wContinue.show_all()
    pbTimeout.set_fraction(new_value)
    # As this is a timeout function, return True so that it
    # continues to get called
    return True


################
#  Set events  #
################

btYes = builder.get_object("btYes")
btYes.connect("clicked",onYesPressed)
btNo = builder.get_object("btNo")
btNo.connect("clicked",onNoPressed)
wTimeout.connect("delete-event",onDeleteWindow)
btBack = builder.get_object("btBackWork")
btBack.connect("clicked",onBackWorkPressed)
pbTimeout = builder.get_object("pbTimeout")


DATEFORMAT='%d/%m/%Y %H:%M'

for task in tw.tasks.filter('+READY +reminder'):
        #get all fields in task
        task.refresh()
        addReminder(task['description'],task['due'].strftime(DATEFORMAT))

# 1 minute = 600 
# 5 minutes = x
if len(sys.argv) >= 2:
    timeout=int(sys.argv[1])
    breaks=int(sys.argv[2])
else:
    timeout=5
    breaks=1

if breaks < 4:
    pbTimeout.set_text("Go away you fool! (Break n:"+str(breaks)+")")
else:
    pbTimeout.set_text("Super rest! ("+str(os.getenv('POMODORO_LTIMEOUT',15))+" minutes)")

GObject.timeout_add(600*timeout, update_timeout_bar)
activity_mode = False

#log break time with timewarrior to know the total free time of today/week/....
subprocess.Popen(['timew', 'start', 'pomodoro_timeout', '+nowork'])
do_timeout()
Gtk.main()

