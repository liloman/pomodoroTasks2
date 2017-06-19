#!/usr/bin/env python

from subprocess import call,PIPE,check_output, Popen
from tasklib import TaskWarrior,Task
import unittest
import shutil
import dbus
import time
import re
import os

dirname, filename = os.path.split(os.path.realpath(__file__))
#change to the project dir
os.chdir(dirname)

class TestPomodoro(unittest.TestCase):
    tw = TaskWarrior(data_location='.task/', create=True)
    new_task = Task(tw, description="task for the test")
    new_task.save()
    uuid = new_task['uuid']



    def get_active_task(self):
        for task in self.tw.tasks.pending():
            if task.active:
                #get all fields in task
                task.refresh()
                return task
        return {}

    def tearDown(self):
        try:
            interface.do_fsm("stop")[0]
        except:
            return

    def start(self):
        self.assertEquals(interface.do_start(dbus.Dictionary({'uuid':  self.uuid , 'resume': 'No'}))[0],"started:"+self.uuid)

    def test_stop(self):
        self.start()
        self.assertEquals(interface.do_fsm("stop")[0],"ok")

    def test_status(self):
        prog = re.compile('stopped .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.start()
        prog = re.compile('started .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.assertTrue(interface.do_fsm("pause")[0])
        prog = re.compile('paused .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))

    def test_done_current(self):
        other_task = Task(self.tw, description="task to be done")
        other_task.save()
        uuid2 = other_task['uuid']
        self.assertEquals(interface.do_start(dbus.Dictionary({'uuid':  uuid2 , 'resume': 'No'}))[0],"started:"+uuid2)
        prog = re.compile('started .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.assertEquals(interface.done_current()[0],"ok")
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.assertEquals(interface.done_current()[0],"no active task")

    def test_resume(self):
        self.start()
        self.assertEquals(interface.do_fsm("stop")[0],"ok")
        self.assertEquals(interface.do_fsm("start")[0],"ok")
        prog = re.compile('started .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.assertEquals(interface.do_fsm("pause")[0],"ok")
        prog = re.compile('paused .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.assertEquals(interface.do_fsm("start")[0],"ok")
        self.assertEquals(interface.do_fsm("start")[0],"Already started")
        # test done and resume
        other_task = Task(self.tw, description="task 2 for the test")
        other_task.save()
        uuid2 = other_task['uuid']
        self.assertEquals(interface.do_start(dbus.Dictionary({'uuid':  uuid2 , 'resume': 'No'}))[0],"started:"+uuid2)
        prog = re.compile('started .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.assertEquals(interface.do_fsm("stop")[0],"ok")
        other_task.done()
        self.assertEquals(interface.do_fsm("start")[0],"ok")
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        # test delete and resume
        other_task = Task(self.tw, description="task 3 for the test")
        other_task.save()
        uuid2 = other_task['uuid']
        self.assertEquals(interface.do_start(dbus.Dictionary({'uuid':  uuid2 , 'resume': 'No'}))[0],"started:"+uuid2)
        prog = re.compile('started .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        self.assertEquals(interface.do_fsm("stop")[0],"ok")
        other_task.delete()
        self.assertEquals(interface.do_fsm("start")[0],"ok")
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))

    def test_reset(self):
        self.start()
        # from start to reset with previous task 
        self.assertEquals(interface.do_fsm("reset")[0],"ok")
        prog = re.compile('started .* left.*')
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))
        # from pause to reset with previous task 
        self.assertEquals(interface.do_fsm("pause")[0],"ok")
        self.assertEquals(interface.do_fsm("reset")[0],"ok")
        self.assertTrue(prog.match(interface.do_fsm("status")[0]))

    def test_warning(self):
        self.assertEquals(interface.do_fsm("stop")[0],"Already stopped")
        self.start()
        self.assertEquals(interface.do_fsm("start")[0],"Already started")
        self.assertEquals(interface.do_fsm("pause")[0],"ok")
        # doing a resume so
        self.assertEquals(interface.do_fsm("pause")[0],"ok")

    # close the daemon last
    def test_zzz(self):
        self.new_task.delete()
        # remove the directory
        shutil.rmtree('.task/')
        interface.do_quit(False)

if __name__ == '__main__':
    Popen(["python", "../daemon.py","test/.task","testing"]) 
    # wait 1 second to bring up the service
    time.sleep(1)
    bus = dbus.SessionBus()
    session_bus = bus.get_object('org.liloman.pomodoro', "/daemon")
    interface = dbus.Interface(session_bus, "org.liloman.pomodoroInterface")
    unittest.main()
