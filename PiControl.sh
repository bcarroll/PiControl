#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_DIR}

start(){
    echo "Starting PiControl" >&2
    python PiControl.py
}

stop(){
    echo "Stopping PiControl" >&2
    sudo ps -ef|grep PiControl|xargs kill
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
