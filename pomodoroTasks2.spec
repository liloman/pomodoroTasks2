Name:		pomodoroTasks2
Version:	0.1
Release:	1%{?dist}
Summary:  Graphical trayicon to pomodoro with taskwarrior/timewarrior
Group:		User Interface/X
BuildArch:  noarch
License:	GPLv3
URL:		 https://github.com/liloman/pomodoroTasks2
#must be without *-1.tar.gz to build in copr ¿?
Source0:    %{url}/archive/%{name}-%{version}.tar.gz


Requires:	timewarrior
Requires:	task
Requires:	python-pip
Requires:	dbus-python
Requires:	python-gobject


%description

Pomodoro technique allows you to concentrate on the current task and take short breaks meanwhile works. If you join it with a task manager alike taskwarrior you can have a complete workflow, accounting the time spend on any task meanwhile you take the proper rests for your brain, body (eyes in special), and life. :)
All your work is timetracked with timewarrior so you can view what have you been working anytime easily.


%prep 
%setup -q 

%build
exit 0

%install

mkdir -p %{buildroot}%{_defaultdocdir}/%{name}
cp -a *.md CHANGELOG extras/technique.pdf %{buildroot}%{_defaultdocdir}/%{name}
mkdir -p  %{buildroot}%{_datadir}/%{name}
cp -a pomodoro*.py do_timeout.py images gui test extras %{buildroot}%{_datadir}/%{name}


%files
%doc %{_defaultdocdir}/*
%{_datadir}/*
%exclude %{_datadir}/%{name}/*/*.pyc
%exclude %{_datadir}/%{name}/*/*.pyo


%post
/usr/bin/pip install tasklib -q || :
#create taskwarrior/timewarrior databases if empties
#executed as $USER
for user in /home/*; do
   su - ${user##*/} -c 'task <<< yes' &> /dev/null || :
   su - ${user##*/} -c 'timew <<< yes' &> /dev/null || :
done
if [[ -d /usr/share/bash-completion/completions/ ]]; then
    cp extras/pomodoro-client.bash_autocompletion /usr/share/bash-completion/completions/pomodoro-client.py
fi
#install user hooks
for user in /home/*; do
   su - ${user##*/} -c '%{_datadir}/%{name}/extras/prepare_hooks.sh install' &> /dev/null || :
done

#link pomodoro binaries to _bindir (/usr/bin/)
ln -sf %{_datadir}/%{name}/pomodoro-*.py %{_bindir} 
#link add-reminder.sh to _bindir
ln -sf %{_datadir}/%{name}/extras/add-reminder.sh %{_bindir} 

%postun
#remove python tasklib 
/usr/bin/pip uninstall tasklib -qy || :
#remove symlinks
rm -f /usr/bin/pomodoro-*.py /usr/bin/add-reminder.sh || :
#remove bash autocompletion
rm -f /usr/share/bash-completion/completions/pomodoro-client.py || :
#remove user hooks
for user in /home/*; do
   su - ${user##*/} -c '%{_datadir}/%{name}/extras/prepare_hooks.sh uninstall' &> /dev/null || :
done


