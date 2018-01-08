#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_DIR}

start(){
    python PiControl.py
}

stop(){
    sudo ps -ef|grep PiControl|xargs kill
}

restart(){
    stop()
    counter=1
    while [$counter -le 5]
    do
        sleep(1)
        ((counter++))
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
