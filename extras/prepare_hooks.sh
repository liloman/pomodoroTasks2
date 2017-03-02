#!/usr/bin/env bash
#Install/uninstall the timewarrior hooks and systemd service for pomodoroTasks2

install() {
    local datadir=${1:-/usr/share/pomodoroTasks2}
    create () {
        local dir=$1
        [[ -d $dir ]] || mkdir -p "$dir"
    }

    echo "Creating taskwarrior hook for on-modify.timewarrior"
    create ~/.task/hooks
    ln -svf $datadir/extras/on-modify.timewarrior ~/.task/hooks/

    echo "Creating timewarrior work report"
    create ~/.timewarrior/extensions/
    ln -svf $datadir/extras/work.py ~/.timewarrior/extensions/

    echo "Creating systemd user service to stop current task on logout"
    create ~/.config/systemd/user/ 
    cp -v $datadir/extras/stop-task-on-logout.service  ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable stop-task-on-logout.service
    systemctl --user start  stop-task-on-logout.service
}

uninstall() {
    echo "Removing taskwarrior hook for on-modify.timewarrior"
    rm -f ~/.task/hooks/on-modifiy.timewarrior

    echo "Removing timewarrior work report"
    rm -f ~/.timewarrior/extensions/work.py 

    echo "Removing systemd user service to stop current task on logout"
    systemctl --user stop stop-task-on-logout.service
    rm -f ~/.config/systemd/user/stop-task-on-logout.service
    systemctl --user daemon-reload
}

if [[ $1 == install ]]; then 
    install $2
elif [[ $1 == uninstall ]]; then 
    uninstall
else
    echo "Incorrect option:\"$1\" must pass install or uninstall"
fi
