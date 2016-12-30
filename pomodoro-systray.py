#!/usr/bin/env python

# For dbus
import dbus
import dbus.service
import dbus.mainloop.glib
import threading
import subprocess

import sys
import re
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk,GObject
from tasklib import TaskWarrior, Task

builder = Gtk.Builder()

class PomodoroApp(dbus.service.Object):
    bus_name = "org.liloman.pomodoro.systray"
    state = ""

    def __init__(self, rc = '~/.task'):
        self.tw = TaskWarrior(data_location=rc, create=True)
        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_file("images/iconStarted-0.png")
        self.status_icon.connect("popup-menu", self.right_click_event)
        self.status_icon.connect("activate", self.left_click_event)
        # systray daemon
        name = dbus.service.BusName(self.bus_name, bus=dbus.SessionBus(),do_not_queue=True, replace_existing=False, allow_replacement=False )
        dbus.service.Object.__init__(self, name, '/systray')
        # client for daemon
        bus = dbus.SessionBus(private = True)
        daemon_client = bus.get_object('org.liloman.pomodoro', "/daemon")
        self.interface = dbus.Interface(daemon_client, "org.liloman.pomodoroInterface")


    @dbus.service.method("org.liloman.pomodoro.systrayInterface", in_signature='', out_signature='')
    def show_change_task(self):
        self.showChangeTask(Gtk.ImageMenuItem())


    # to be called from the daemon 
    @dbus.service.method("org.liloman.pomodoro.systrayInterface", in_signature='', out_signature='')
    def quit(self):
        Gtk.main_quit()

    # a{ss} = dictionary(dbus) of keys=s and values=s
    @dbus.service.method("org.liloman.pomodoro.systrayInterface", in_signature='a{ss}', out_signature='as')
    def set_state(self, dic):
        self.state = dic['state']
        self.status_icon.set_from_file(dic['icon'])
        self.status_icon.set_tooltip_text(dic['tooltip'])
        return ["set_state"]

    #Have to use this thread cause otherwise dbus/gtk will hang for a while ????
    def  _fsm(self,action):
        print ("reply:"+self.interface.do_fsm(action)[0])

    def left_click_event(self,icon):
        threading.Thread(target=self._fsm,args=['pause']).start()

    def status(self):
        threading.Thread(target=self._fsm,args=['status']).start()


    #Shows the form to change the current task
    def showChangeTask(self,ImageMenuItem):
        # subform to create a new task
        def showAddTask(widget):
            def AddTask(widget):
                # decode and trim the text to not allow only whitespaces/tabs
                desc = eDescription.get_text().decode('utf-8').strip()
                proj = eProject.get_text().decode('utf-8').strip() 
                if desc:
                    new_task = Task(self.tw)
                    new_task['description'] = desc
                    if proj and proj != 'None':
                        new_task['project'] = proj
                    # write it down
                    new_task.save()
                    # update the comboboxtext of pending tasks
                    uuids[new_task['id']]=str(new_task['uuid'])
                    desc=u''.join(new_task['description']).encode('utf-8').strip() 
                    proj=u''.join(new_task['project']).encode('utf-8').strip() 
                    line=str(new_task['id'])+" ["+str(proj)+"]-"+desc
                    cbChange.append_text(line)
                    # select the new one
                    cbChange.set_active(len(uuids)-1)
                    wAddTask.hide()
                else:
                    # should write a custom css to change the color
                     # https://developer.gnome.org/gtk3/stable/GtkWidget.html#gtk-widget-override-color
                    eDescription.grab_focus()

            def closeAddTask(widget):
                wAddTask.hide()

            #buttons
            btCancelAdd = builder.get_object("btCancelAdd")
            btCancelAdd.connect("clicked",closeAddTask)
            btAdd= builder.get_object("btAdd")
            btAdd.connect("clicked",AddTask)
            #entries
            eDescription = builder.get_object("eDescription")
            eProject     = builder.get_object("eProject")
            cbProject    = builder.get_object("cbProject")
            lbDescription = builder.get_object("lbDescription")

            projects = set(['None'])
            for task in self.tw.tasks:
                try:  
                    task.refresh()
                    if task['project']:
                        projects.add(u''.join(task['project']).encode('utf-8').strip())
                except:
                    next

            cbProject.remove_all()
            for project in sorted(projects):
                cbProject.append_text(project)
            cbProject.set_active(0)
            wAddTask.show()

        def closeChangeTask(widget):
            wChangeTask.hide()

        #Have to use this thread cause otherwise dbus/gtk will hang for a while ????
        def _do_start(uuid, resume):
            dic = dbus.Dictionary({'uuid':uuid , 'resume': resume } , signature = 'ss' )
            print ("reply:"+self.interface.do_start(dic)[0])

        def do_start(uuid,resume = 'No'):
            threading.Thread(target=_do_start,args=[uuid, resume]).start()

        #Have to use this thread cause otherwise dbus/gtk will hang for a while ????
        def _done_current():
            print ("reply:"+self.interface.done_current()[0])

        def done_current():
            threading.Thread(target=_done_current,args=[]).start()

        def ChangeTask(widget):
            sel = cbChange.get_active_text()
            m = re.search('()\d+',sel)
            id = int(m.group(0))
            if ckbDone.get_active():
                done_current()
            # start even if not selected any task
            do_start(uuids[id], 'Yes')
            wChangeTask.hide()

        uuids = { 0: '0'}
        builder.add_from_file("gui/change_task.glade")
        wChangeTask = builder.get_object("wChangeTask")
        cbChange    = builder.get_object("cbChange")
        ckbDone     = builder.get_object("ckbDone")
        wAddTask    = builder.get_object("wAddTask")
        #buttons
        btAddTask = builder.get_object("btAddTask")
        btAddTask.connect("clicked",showAddTask)
        btCancelChangeTask = builder.get_object("btCancelChangeTask")
        btCancelChangeTask.connect("clicked",closeChangeTask)
        btChange = builder.get_object("btChangeTask")
        btChange.connect("clicked",ChangeTask)
        # set the combobox
        cbChange.remove_all()
        cbChange.append_text('0 -------------- None ------------ ')
        cbChange.set_active(0)

        #fill the combobox
        for task in self.tw.tasks.pending():
            if not task.active:
                task.refresh()
                desc=u''.join(task['description']).encode('utf-8').strip() 
                proj=u''.join(task['project']).encode('utf-8').strip() 
                line=str(task['id'])+" ["+str(proj)+"]-"+desc
                uuids[task['id']]=str(task['uuid'])
                cbChange.append_text(line)
        wChangeTask.show()

    def right_click_event(self, icon, button, time):

        def _quit_daemon():
            self.interface.quit()

        def quit_daemon():
            threading.Thread(target=_quit_daemon,args=[]).start()

        def quit(ImageMenuItem):
            quit_daemon()
            Gtk.main_quit()

        #the funcs must be declared before menu.append use
        def do_reset(ImageMenuItem):
            threading.Thread(target=self._fsm,args=['reset']).start()

        def do_stop(ImageMenuItem):
            threading.Thread(target=self._fsm,args=['stop']).start()

        def take_a_break(ImageMenuItem):
            threading.Thread(target=self._fsm,args=['take_break']).start()

        def create_menu_item(label, icon_name):
            image = Gtk.Image()
            image.set_from_icon_name(icon_name, 24)
            item = Gtk.ImageMenuItem()
            item.set_label(label)
            item.set_image(image)
            return item  

        def connect_menu_item(label, icon_name, event):
            item = create_menu_item(label, icon_name)
            item.connect("activate", event)
            return item

        self.menu = Gtk.Menu()

        self.menu.append(connect_menu_item("Change task", "edit-paste", self.showChangeTask))
        self.menu.append(connect_menu_item("Reset", "edit-redo", do_reset))
        self.menu.append(connect_menu_item("Stop", "process-stop", do_stop))
        self.menu.append(connect_menu_item("Take a break", "alarm-symbolic", take_a_break))
        self.menu.append(connect_menu_item("Close app", "application-exit",quit))

        self.menu.show_all()
        self.menu.popup(None, None, None, self.status_icon, button, time)



        
if __name__ == '__main__':
    #enable gtk's c-threads before glib main loop
    GObject.threads_init()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = GObject.MainLoop()


    try:
       if len(sys.argv) == 2:
           app = PomodoroApp(sys.argv[1])
       else:
           app = PomodoroApp()
    except:
       print "No pomodoro daemon found"
       sys.exit(1)


    # dbus loop
    thread = threading.Thread(target=loop.run)
    thread.daemon = True
    thread.start()

    #update the trayicon
    app.status()

    #must be in the main thread
    Gtk.main()
