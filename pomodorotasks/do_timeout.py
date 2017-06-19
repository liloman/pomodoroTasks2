#!/usr/bin/env python
#Timeout screen

from __future__ import print_function
from builtins import str
from builtins import object
import dbus
import dbus.service
import subprocess

import sys
import os
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject
from tasklib import TaskWarrior 


class PomodoroTimeout(object):

    def __init__(self):
        self.tw = TaskWarrior()
        builder.add_from_file("gui/timeout.glade")
        self.wTimeout     = builder.get_object("wTimeout")
        self.pbTimeout    = builder.get_object("pbTimeout")
        self.wContinue    = builder.get_object("wContinue")
        self.lsbReminders = builder.get_object("lsbReminders")
        self.bus = dbus.SessionBus()
        self.session_bus = self.bus.get_object('org.liloman.pomodoro', "/daemon")
        self.interface = dbus.Interface(self.session_bus, "org.liloman.pomodoroInterface")

        ################
        #  Set events  #
        ################

        self.btYes = builder.get_object("btYes")
        self.btYes.connect("clicked",self.onYesPressed)
        self.btNo = builder.get_object("btNo")
        self.btNo.connect("clicked",self.onNoPressed)
        self.wTimeout.connect("delete-event",self.onDeleteWindow)
        self.btBack = builder.get_object("btBackWork")
        self.btBack.connect("clicked",self.onBackWorkPressed)
        self.pbTimeout = builder.get_object("pbTimeout")

        DATEFORMAT='%d/%m/%Y %H:%M'
        for task in self.tw.tasks.filter('+READY +reminder'):
                #get all fields in task
                task.refresh()
                self.addReminder(task['description'],task['due'].strftime(DATEFORMAT))

    ###############
    #  Reminders  #
    ###############


    def update_reminders(self):
        i=0
        for task in self.tw.tasks.filter('+READY +reminder'):
            # for each box 
            if self.lsbReminders.get_row_at_index(i):
                for box in self.lsbReminders.get_row_at_index(i).get_children():
                    #get the done checkbox
                    if box.get_children()[2].get_active():
                        #mark as done the reminder 
                        #dont call the hook and track with timew?
                        task.done()
            i+=1

    def addReminder(self,desc,date):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        ldesc = Gtk.Label(desc, xalign=0)
        ldate = Gtk.Label(date, xalign=0)
        cdone = Gtk.CheckButton()
        hbox.pack_start(ldesc, True, True, 0)
        hbox.pack_start(ldate, False, True, 0)
        hbox.pack_start(cdone, False, True, 0)
        self.lsbReminders.add(row)

    #############
    #  Events   #
    #############

    def onYesPressed(self,w):
        subprocess.Popen(['timew', 'stop'])
        print (self.interface.do_fsm("start")[0])
        self.wContinue.destroy()
        Gtk.main_quit()  

    def onNoPressed(self,w):
        subprocess.Popen(['timew', 'stop'])
        self.wContinue.destroy()
        Gtk.main_quit()  

    def onDeleteWindow(self,*args):
        self.update_reminders()
        self.wContinue.show_all()

    def onBackWorkPressed(self,w):
        self.update_reminders()
        subprocess.Popen(['timew', 'stop'])
        print (self.interface.do_fsm("start")[0])
        Gtk.main_quit()

    def do_timeout(self):
        self.wTimeout.show_all()

    def update_timeout_bar(self):
        new_value = self.pbTimeout.get_fraction() + 0.01
        if new_value > 1:
            new_value = 0
            self.update_reminders()
            self.wTimeout.destroy()
            self.wContinue.show_all()
        self.pbTimeout.set_fraction(new_value)
        # As this is a timeout function, return True so that it
        # continues to get called
        return True




if __name__ == '__main__':

    builder = Gtk.Builder()

    timeout = PomodoroTimeout()

    if len(sys.argv) >= 2:
        break_time=int(sys.argv[1])
        breaks=int(sys.argv[2])
    else:
        break_time=5
        breaks=1


    if breaks < 4:
        timeout.pbTimeout.set_text("Go away you fool! (Break n:"+str(breaks)+")")
    else:
        timeout.pbTimeout.set_text("Super rest! ("+str(os.getenv('POMODORO_LTIMEOUT',15))+" minutes)")

    # 1 minute = 600 
    # 5 minutes = x
    GObject.timeout_add(600*break_time, timeout.update_timeout_bar)

    #log break time with timewarrior to know the total free time of today/week/....
    subprocess.Popen(['timew', 'start', 'pomodoro_timeout', '+nowork'])

    #Splash!!
    timeout.do_timeout()

    Gtk.main()

