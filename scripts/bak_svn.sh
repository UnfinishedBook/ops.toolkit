#!/bin/bash
#0 4 * * * /bin/svn_bak.sh >> /var/log/svn_bak.log 2>&1

SRC=/mydata/svn/chcf
DST=/backup/svn/`date +%F`
echo "`date '+%F %T'` backup $SRC to $DST"
svnadmin hotcopy $SRC $DST

DEL=/backup/svn/`date -d '-5 days' +%F`
if [ -d $DEL ]; then
    echo "`date '+%F %T'` delete $DEL"
    rm -rf $DEL
else
    echo "`date '+%F %T'` not found $DEL"
fi

echo "`date '+%F %T'` over"

