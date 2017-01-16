
Don't make any excuse anymore to not use the [Pomodoro Technique wikipedia](https://en.wikipedia.org/wiki/Pomodoro_Technique) or [The Pomodoro Technique ](technique.pdf)!

Pomodoro technique allows you to concentrate on the current task and take short breaks meanwhile works.
If you get that and join it with a task manager alike taskwarrior (or any other) you can have a complete workflow, accounting the time spend on any task meanwhile you take the proper rests for your brain, body, life and eyes. :)

A previous "week" hack project.


Table of Contents
=================

  * [INSTALL](#INSTALL)
     * [1. Taskwarrior dependencies (python based)](#1-taskwarrior-dependencies-python-based)
     * [2. Timewarrior](#2-timewarrior)
     * [3. Pomodoro](#3-pomodoro)
  * [Why timewarrior?](#why-timewarrior)
  * [Screenshots](#screenshots)
  * [Spec](#spec)
  * [TODO](#todo)
  * [FIXED](#fixed)



###INSTALL 

####1. Taskwarrior dependencies (python based)

```bash
pip install tasklib --user
sudo dnf/apt-get/whatever install taskwarrior/task/whatever
task (answer yes to create the database)
```

#### 2. Timewarrior

```bash
sudo dnf/apt-get/whatever install build-essential cmake 
git clone --recursive https://git.tasktools.org/scm/tm/timew.git timew.git
cd timew.git
git checkout master 
cmake -DCMAKE_BUILD_TYPE=release .
make
sudo make install
timew (answer yes to create the database)
```

####3. Pomodoro

```bash
git clone https://github.com/liloman/pomodoroTasks2
cd pomodoroTasks2/
./pomodoro-daemon.py
```

You can customize the working time and the break times (short and long), just exporting a few ENV variables on your ~/.bashrc/whatever.

```bash
#default pomodoro session (minutes)
export POMODORO_TIMEOUT=25
#default pomodoro short break (minutes)
export POMODORO_STIMEOUT=5
#default pomodoro long break (minutes)
export POMODORO_LTIMEOUT=15
```


So just launch the pomodoro-daemon.py and you are ready to go, feel free to add it in ~/.local/bin,autostart,systemd,... :)


### Why timewarrior?

Because you the objective is track all your workflow and nothing better for that purpose than the newcomer taskwarrior brother timewarrior. :)

If you wish to track every task of taskwarrior in timewarrior you need to:

1. Copy/link [this taskwarrior hook](https://github.com/liloman/warriors/blob/master/on-modify.timewarrior) into ~/.task/hooks directory 

 So it will be: 

 ```bash
 cd ~/.task/hooks
 wget https://raw.githubusercontent.com/liloman/warriors/master/on-modify.timewarrior
 chmod u+x on-modify.timewarrior
 ```

 And for now on each time you start/stop a task it will be tracked with timewarrior unless it contains the +notimew tag. ;) 

2. To stop tracking when you logout/shutdown (I recommend it), you have to copy/link a [a systemd user unit](https://github.com/liloman/dotfiles/blob/master/systemd/.config/systemd/user/on-logout.service)

 So as simple as: 
 
 ```bash
 cd ~/.config/systemd/user/ || mkdir -p ~/.config/systemd/user/
 wget https://raw.githubusercontent.com/liloman/dotfiles/master/systemd/.config/systemd/user/on-logout.service
 systemctl --user daemon-reload
 systemctl --user start on-logout.service
 ```

3. Everytime that there's a pomodoro timeout the app automatically track the time with timewarrior so you don't have to worry about that ;)

4. If you want to track also the time the PC is off (I don't recommend it if you have several PCs and sync your tasks among them) you can execute after every log [this script](https://github.com/liloman/warriors/blob/master/last-boots.sh)

 So it will be: 
 
 ```bash
 cd your-autostart-dir/xinit/systemd/whatever/...
 wget https://raw.githubusercontent.com/liloman/warriors/master/last-boots.sh
 chmod u+x last-boots.sh
 
 ```

5. If you want (I recommend it) to know how much time have you work today/this week/month/whatever, you need to create a new timewarrior report like [this](https://github.com/liloman/warriors/blob/master/work.py)

 So just do:
 
 ```bash
 cd .timewarrior/extensions/
 wget https://raw.githubusercontent.com/liloman/warriors/master/work.py
 chmod u+x work.py
 ```
 This report will show you all your work except the tasks with +nowork tag. ;)


 You can create these two aliases for cozyness in your ~/.bashrc/whatever I can guarantee that you will use them ;)
 
 
 ```bash
 alias twt='timew work today'
 alias tww='timew work :week'
 ```
 
6. Start enjoying timewarrior!. :) 


 How much have I been working today? 
 
 ```bash
 prompt>twt
 Total by Tag from 2017-01-15 23:00:00 - 2017-01-16 09:59:28 (sorted by time)
 
 Tag                                                Total
  ----------------------------------       ---------------
 
 More stuff / pro:stuff                   0 days, 2:14:00
 Doing demo / pro:dev.demo                0 days, 3:04:49
                                         ----------------                   
 Total                                    0 days, 5:18:49
 
 ```

 Umm, 5:18 hours. Niiiiiiiiiiice. 
 
 So no remorse of conscience for today. ;)
 
 Of course you could know how much have you worked this week for a project for example:
 
 ```bash
  prompt>tww pro:awesome
 Total by Tag from 2017-01-08 23:00:00 - 2017-01-15 23:00:00 (sorted by time)
 
 Tag                                                Total
 ----------------------------------       ---------------
 
 Fixing that bugs 1/ pro:awesome          0 days, 0:14:00
 Fixing that bugs 2 / pro:awesome         1 days, 2:14:00
 Writing docs / +docs / pro:awesome       3 days, 3:04:49
                                         ----------------                   
 Total                                    4 days, 5:32:49
 
 ```

###Screenshots

Relax time:

![25 minutes passed](images/screenshots/timer1.png "25 minutes passed")

Back to work:

![Back to work?](images/screenshots/timer2.png "Back to work?")

Menu:

![Started with tooltip](images/screenshots/started.png "Started with tooltip")

![Paused with menu](images/screenshots/paused.png "Paused with menu")

All trayicons:

![All icons](images/screenshots/all-icons.png "All icons")

Change current task:

![Change Task](images/screenshots/changeTask.png "Change task")

![Change Task 2](images/screenshots/changeTask2.png "Change task 2")

Add new task:

![Add new Task](images/screenshots/addTask.png "Add new Task")



###Spec

Minimalistic implementation with FSM (Finite State Machine) and some dbus niceness. :)


###TODO

- [x] dbus 
- [x] Timewarrior integration to track the complete lifespan of your computer. ;)
- [x] Dont wait a minute to refresh the trayicon when used the cli
- [ ] Unit testing \(fix travis install ... \)

###FIXED

1. ~~Linux mint issues~~
