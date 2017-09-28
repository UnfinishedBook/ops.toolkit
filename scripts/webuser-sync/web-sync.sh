#!/bin/bash
#param: wap / cdn

if [ "$1" == "wap" ]; then
    obj_dir=/mydata/wap
elif [ "$1" == "cdn" ]; then
    obj_dir=/mydata/cdn
else
    echo "bad param"
    exit 0
fi

obj_id1=10.104.11.150
src_dir=/mydata/maintenance/webuser/$1
watch_file=/mydata/maintenance/webuser/${1}.sync.txt

while true
do
    #监听目录的变更事件，排除vim的临时文件
    #inotifywait -r $src_dir -e modify,move,create --exclude '(.swp|.swx)' --timefmt '%Y-%m-%d %H:%M' --format '%T %e %w %f'
    #sleep 2
    #增量同步，排除隐藏文件
    #rsync -azv -e 'ssh -i /root/.ssh/id_rsa_webuser' --exclude='.*' $src_dir/ webuser@$obj_id1:$obj_dir/

    #只监听一个文件
    inotifywait $watch_file -e modify --timefmt '%Y-%m-%d %H:%M' --format '%T %e %w %f'
    if [ "$?" == "0" ]; then
        sleep 1
        echo `date` "开始增量同步($src_dir/)到($obj_id1:$obj_dir/)"
        rsync -azv -e 'ssh -i /root/.ssh/id_rsa_webuser' --exclude='.*' $src_dir/ webuser@$obj_id1:$obj_dir/
        echo `date` "清除已同步的内容"
        rm -rf $src_dir/*
    else
        echo `date` "监听出现错误，稍后重试..."
        sleep 10
    fi
done

