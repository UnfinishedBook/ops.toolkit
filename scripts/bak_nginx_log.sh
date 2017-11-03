#!/bin/bash
#0 4 * * * /bin/bak_nginx_log.sh >> /var/log/bak_nginx_log.log 2>&1

echo -e "Start at \c"
date '+%F %T'

LOG_DIR=/mydata/tengine/log
BAK_DIR=/mydata/maintenance/backup/logs/tengine

list=`find $LOG_DIR -name '*.log' -mtime +10`
count=`echo $list | wc -w`
n=$count
for file in $list
do
    fn=${file##*/}
    dir=${file%/*}
    bak_fn=${fn}.tar.gz
    bak_dir=$BAK_DIR/${dir##*$LOG_DIR/}
    if [ ! -d $bak_dir ]; then
        mkdir -p $bak_dir
    fi
    echo "[$n/$count] backup $dir/$fn to $bak_dir/$bak_fn"
    let n=n-1
    tar -zcf $bak_dir/$bak_fn -C $dir $fn --remove-files
done

echo "开始清理超过90天的日志备份,除去quickbid/api/qbpay三者"
EXPIRE_BAK=`find $BAK_DIR -name *.tar.gz -mtime +90 | grep -Ev "quickbid|api|qbpay" | sort`
EXPIRE_BAK_NUM=`echo $EXPIRE_BAK | wc -w`
rm -rf $EXPIRE_BAK
echo -e "成功清理超过90天的日志备份${EXPIRE_BAK_NUM}个:  \n$EXPIRE_BAK"

echo -e "Finish at \c"
date '+%F %T'

