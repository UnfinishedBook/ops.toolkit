#!/bin/bash

cd `dirname $0`
cd ..
DEPLOY_DIR=`pwd`
SERVER_NAME=ops.toolkit.http
EXE_FILE=$DEPLOY_DIR/http.py
LOG_DIR=/mydata/maintenance/logs

function start()
{
    PIDS=`ps -ef | grep python | grep "$EXE_FILE" |awk '{print $2}'`
    if [ -n "$PIDS" ]; then
        echo "ERROR: The $SERVER_NAME already started!"
        echo "PID: $PIDS"
        exit 1
    fi
    nohup ssh-agent $EXE_FILE > $LOG_DIR/ops-toolkit-http.std 2>&1 &
}

function stop()
{
    PIDS=`ps -ef | grep python | grep "$EXE_FILE" |awk '{print $2}'`
    if [ -z "$PIDS" ]; then
        echo "ERROR: The $SERVER_NAME not started!"
    else
        kill -9 $PIDS
    fi
}


if [ "$1" == "start" ];then
    start
elif [ "$1" == "stop" ];then
    stop
elif [ "$1" == "restart" ];then
    stop
    sleep 3
    start
else
    echo "http.sh [start/stop/restart]"
fi

