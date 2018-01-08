#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_DIR}

start(){
    echo "Starting PiControl"
    python PiControl.py
}

stop(){
    echo "Stopping PiControl"
    sudo ps -ef|grep PiControl|xargs kill
}

restart(){
    echo "Restarting PiControl"
    stop()
    counter=1
    sleep(3)
    done
    start()
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
esac
