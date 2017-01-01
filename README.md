
Don't make any excuse anymore to not use the [Pomodoro Technique](https://en.wikipedia.org/wiki/Pomodoro_Technique)!


###Info

Pomodoro technique allows you to concentrate on the current task and take short breaks meanwhile works.
If you get that and join it with a task manager alike taskwarrior (or any other) you can have a complete workflow, accounting the time spend on any task meanwhile you take the proper rests for your brain, body, life and eyes. :)

A previous "week" hack project.


###Dependencies (python based)

1. pip install tasklib --user
2. apt-get/dnf/whatever install python-dbus/dbus-python/... (if not already...)
3. taskwarrior and timewarrior


###Why yet another pomodoro app?

There isn't anything with taskwarrior alike for linux AFAIK.  :o:

###Screenshots

Relax time:

![25 minutes passed](images/screenshots/timer1.png "25 minutes passed")

Back to work:

![Back to work?](images/screenshots/timer2.png "Back to work?")

Trayicon:


![Started with tooltip](images/screenshots/started.png "Started with tooltip")

![Paused with menu](images/screenshots/paused.png "Paused with menu")

![Stopped](images/screenshots/stopped.png "Stopped")


![Change Task](images/screenshots/changeTask.png "Change task")

![Change Task 2](images/screenshots/changeTask2.png "Change task 2")

![Add new Task](images/screenshots/addTask.png "Add new Task")


###Install 

You can customize the working time and the break times (short and long), just exporting a few ENV variables.

In my case (same as default):

```bash
#default pomodoro session (minutes)
export POMODORO_TIMEOUT=25
#default pomodoro short break (minutes)
export POMODORO_STIMEOUT=5
#default pomodoro long break (minutes)
export POMODORO_LTIMEOUT=15
#Launch pomodoroTasks2 (daemon) 
~/.local/bin/pomodoro-daemon.py
```

So just launch the pomodoro-daemon.py and you are ready to go, feel free to add it on autostart/systemd/... :)

###Spec

Minimalistic implementation with FSM (Finite State Machine) and some dbus niceness. :)


###TODO

- [x] dbus 
- [x] Timewarrior integration to track the complete lifespan of your computer. ;)
- [x] Dont wait a minute to refresh the trayicon when used the cli
- [ ] Unit testing \(fix travis install ... \)

###FIXED

1. ~~nothing for now~~
