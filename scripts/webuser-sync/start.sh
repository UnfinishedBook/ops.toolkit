#!/bin/bash

deploy=`dirname $0`
cd $deploy
deploy=`pwd`
exefile=$deploy/web-sync.sh

pids=`pidof -x $exefile`
if [ "$pids" != "" ]; then
    echo "this program [$pids] is running ..."
    exit 0
fi

logdir=/mydata/maintenance/webuser/logs
if [ ! -d $logdir ]; then
    mkdir -p $logdir
fi

nohup $exefile wap > $logdir/wap.log 2>&1 &
nohup $exefile cdn > $logdir/cdn.log 2>&1 &

echo "started"

