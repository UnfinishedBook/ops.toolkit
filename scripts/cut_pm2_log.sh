#!/bin/bash
#0 4 * * * /bin/cut_pm2_log.sh >> /var/log/cut_pm2_log.log 2>&1

echo -e "Start at \c"
date '+%F %T'

LOG_DIR=/mydata/logs

list=`find $LOG_DIR -name '*.log' -size +200M | grep -E '/activity-api/|/ad-api/|/ad_stats/|/api/|/auth/|/cms/|/cmsTimer/|/data/' | grep -v 'rename'`
count=`echo $list | wc -w`
tm=`date '+%F'`
n=$count
for file in $list
do
    cutfile=${file%.log*}-rename-${tm}.log
    mv ${file} ${cutfile}
    touch ${file}
    echo "[$n/$count] 重命名 ${file} 为 ${cutfile}"
    let n=n-1
done
/usr/local/bin/pm2 reloadLogs

echo -e "Finish at \c"
date '+%F %T'

