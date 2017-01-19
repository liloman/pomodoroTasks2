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

Pomodoro technique allows you to concentrate on the current task and take short breaks meanwhile works. If you join it with a task manager alike taskwarrior you can have a complete workflow, accounting the time spend on any task meanwhile you take the proper rests for your brain, body, life and eyes. :)
All your work is timetracked with timewarrior so you can view where have you been working anytime easily.


%prep 
%setup -q 

%build
exit 0

%install

mkdir -p %{buildroot}%{_defaultdocdir}/%{name}
cp -a *.md CHANGELOG technique.pdf %{buildroot}%{_defaultdocdir}/%{name}
mkdir -p  %{buildroot}%{_datadir}/%{name}
cp -a pomodoro*.py do_timeout.py images gui test %{buildroot}%{_datadir}/%{name}


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
# echo "linking pomodoro binaries"
ln -sf %{_datadir}/%{name}/pomodoro* %{_bindir} 

%postun
/usr/bin/pip uninstall tasklib -qy || :
#remove symlinks
rm -f /usr/bin/pomodoro-* || :

