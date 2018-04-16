#!/bin/bash
#30 6 * * * /bin/bak_dbdata.sh >> /var/log/bak_dbdata 2>&1

echo -e "Start at \c"
date '+%F %T'

LOG_DIR=/mydata/dbdata
BAK_DIR=/mydata/dbdata/backup

list1=`ls $LOG_DIR | grep 'tb_*'`
for l1 in $list1
do
    count=`ls $LOG_DIR/$l1 | wc -w`
    if [ $count -gt 7 ];then
        let count=$count-7 #保留最新的7个,其他压缩备份
        list2=`ls $LOG_DIR/$l1 | sort | head -$count`
        n=$count
        if [ ! -d $BAK_DIR/$l1 ]; then
            mkdir -p $BAK_DIR/$l1
        fi
        for l2 in $list2
        do
            t1=`stat -c %Y $LOG_DIR/$l1/$l2`
            t2=`date +%s`
            if [ $[ $t2 - $t1 ] -lt 86400 ]; then
                echo "$LOG_DIR/$l1/$l2 在24小时内有修改 跳过"
                continue
            fi
            bak_fn=$l2-`date '+%Y%m%d%H%M%S'`.tgz
            tar -zcf $BAK_DIR/$l1/$bak_fn -C $LOG_DIR/$l1 $l2 --remove-files
            echo "[$n/$count] backup $LOG_DIR/$l1/$l2 to $BAK_DIR/$l1/$bak_fn"
            let n=n-1
        done
    else
        echo "$l1下文件夹少于7个,跳过."
    fi
done

echo -e "Finish at \c"
date '+%F %T'

