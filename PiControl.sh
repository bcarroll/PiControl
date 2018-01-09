#!/bin/bash

# Change the RUN_AS_USER variable to the user you want PiControl to run as
RUN_AS_USER="pi"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_DIR}

start(){
    echo "Starting PiControl" >&2
    sudo -u ${RUN_AS_USER} python lib/database_create.py
    sudo -u ${RUN_AS_USER} python PiControl.py &
}

stop(){
    echo "Stopping PiControl" >&2
     pgrep PiControl|xargs kill -9 2>/dev/null
}

restart(){
    echo "Restarting PiControl" >&2
    stop
    sleep 3
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        ;;
esac
