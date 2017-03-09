#!/usr/bin/env bash
#Add a reminder for pomodoroTasks2

#Add a new reminder  
add-reminder() {
    local desc= 
    local opt=
    local recurrence=
    local due wait_days default_days=15

    echo "Select the type of reminder"
    # select mul in "${opts[@]}";do
    select mul in "Recurrent (ex: birthdate)" "NonRecurrent(from date)" "Inmediate(from today!)"; do
        case $mul in
            R*) opt=recurrent; break;;
            N*) opt=nonrecurrent; break;;
            I*) opt=inmediate; break;;
        esac
    done


    read  -p "Description:"  desc

    #if not inmediate
    if [[ $opt != i* ]]; then
        read  -p "Due date (dd/mm/yyyy). Empty for today:"  due
        [[ -z $due ]] && due=today
        local regex='^[0-3][0-9]/[0-1][0-9]/[0-9]{4}$'
        if ! [[ $due =~ $regex || $due == today ]]; then
            echo "due date: $due must have a valid format (dd/mm/yyyy)"; return
        fi
    fi

    if [[ $opt == r* ]]; then
        read  -p "Active before n days of due date (empty for $default_days):"  wait_days
        [[ -z $wait_days ]] && wait_days=$default_days
        wait_days="due-${wait_days}d"
        read  -p "Recurrence (empty for 1y):" recurrence 
        [[ -z $recurrence ]] && recurrence=1years
    elif [[ $opt == n* ]]; then
        if [[ $due != today ]]; then
            read  -p "Active before n days of due date (empty for no wait):"  wait_days
        fi
        [[ -z $wait_days ]] && wait_days=today || wait_days="due-${wait_days}d"
    else #inmediate so no due date
        due=someday
        wait_days=today
    fi


    local make_reminder="task add '$desc' pro:tasks due:$due wait:${wait_days} until:due+1d recur:$recurrence +reminder  rc.dateformat="D/M/Y""
    echo "$make_reminder"
    echo "Are you sure?"
    select yn in Yes No; do
        case $yn in
            Y* ) $make_reminder; break;;
            N* ) echo "Exit."; break;;
        esac
    done
}


add-reminder

