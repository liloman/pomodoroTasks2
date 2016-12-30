#!/usr/bin/env python

import dbus
import sys
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

import time

builder = Gtk.Builder()
builder.add_from_file("gui/timeout.glade")
wTimeout   = builder.get_object("wTimeout")
pbTimeout  = builder.get_object("pbTimeout")
wContinue  = builder.get_object("wContinue")
bus = dbus.SessionBus()
session_bus = bus.get_object('org.liloman.pomodoro', "/daemon")
interface = dbus.Interface(session_bus, "org.liloman.pomodoroInterface")

def onYesPressed(self):
    print (interface.do_fsm("start")[0])
    wContinue.destroy()
    Gtk.main_quit()  

def onNoPressed(self):
    wContinue.destroy()
    Gtk.main_quit()  

def onDeleteWindow(self,*args):
    wContinue.show_all()

def onBackWorkPressed(self):
    print (interface.do_fsm("start")[0])
    Gtk.main_quit()

def do_timeout():
    wTimeout.show_all()

def update_timeout_bar():
    new_value = pbTimeout.get_fraction() + 0.01
    if new_value > 1:
        new_value = 0
        wTimeout.destroy()
        wContinue.show_all()
    pbTimeout.set_fraction(new_value)
    # As this is a timeout function, return True so that it
    # continues to get called
    return True


btYes = builder.get_object("btYes")
btYes.connect("clicked",onYesPressed)
btNo = builder.get_object("btNo")
btNo.connect("clicked",onNoPressed)
wTimeout.connect("delete-event",onDeleteWindow)
btBack = builder.get_object("btBackWork")
btBack.connect("clicked",onBackWorkPressed)
pbTimeout = builder.get_object("pbTimeout")


# 1 minute = 600 
# 5 minutes = x
if len(sys.argv) >= 2:
    timeout=int(sys.argv[1])
    breaks=int(sys.argv[2])
else:
    timeout=5
    breaks=0

if breaks < 4:
    pbTimeout.set_text("Go away you fool! (Break n:"+str(breaks)+")")
else:
    pbTimeout.set_text("Go away you fool! (Long Break!")

GObject.timeout_add(600*timeout, update_timeout_bar)
activity_mode = False

do_timeout()
Gtk.main()

