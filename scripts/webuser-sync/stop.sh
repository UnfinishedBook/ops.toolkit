#!/bin/bash

pids_sync=`ps -ef | grep '/mydata/maintenance/scripts/webuser-sync/web-sync.sh' | grep -v grep | awk '{print $2}'`
#pids_inotify=`ps -ef | grep 'inotifywait -r /mydata/maintenance/webuser' | grep -v grep | awk '{print $2}'`
pids_inotify=`ps -ef | grep 'inotifywait /mydata/maintenance/webuser/' | grep -v grep | awk '{print $2}'`

if [ "$pids_sync" != "" ]; then
    kill -9 $pids_sync
fi
if [ "$pids_inotify" != "" ]; then
    kill -9 $pids_inotify
fi

echo $pids_sync $pids_inotify killed

