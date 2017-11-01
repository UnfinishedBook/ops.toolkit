#!/bin/bash
#0 4 * * * /bin/bak_project_log.sh >> /var/log/bak_project_log.log 2>&1

echo -e "Start at \c"
date '+%F %T'

LOG_DIR=/mydata/logs
BAK_DIR=/mydata/maintenance/backup/logs

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

echo "开始清理空目录"
EMP_DIR=`find $LOG_DIR -type d -empty | sort`
EMP_DIR_NUM=`echo $EMP_DIR | wc -w`
rm -rf $EMP_DIR
echo -e "成功清理空目录${EMP_DIR_NUM}个:  \n$EMP_DIR"

echo -e "Finish at \c"
date '+%F %T'

