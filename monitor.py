#!/usr/bin/python  
# -*- coding: UTF-8 -*-

import os
import sys

if len(sys.argv)<4 or (sys.argv[1]!='qb' and sys.argv[1]!='db') or (sys.argv[2]!='job' and sys.argv[2]!='queue') or (sys.argv[3]!='--discover' and sys.argv[3]!='--updata'):
    print '''usage:
    monitor.py <qb/db> <job/queue> <--discover/--updata>
    '''
    exit()

if sys.argv[1] == 'qb':
    os.environ['ops_project'] = 'quickbid'
    host = 'shanpai.monitor'
else:
    os.environ['ops_project'] = 'duobao'
    host = 'duobao.monitor'
os.environ['ops_key'] = 'maintenance'

from gl import *
from wrap import *

env = 'pro'
GL.setEnv(env)

(zabbix_job,zabbix_queue) = zabbix_monitor()
seq = ','

if sys.argv[2] == 'job':
    data = {"data": zabbix_job.values()}
    if sys.argv[3] == '--updata':
        lines = []
        line = '%s monitor_jobs_count %d\n' % (host, len(data['data']))
        lines.append(line)
        for tt in data['data']:
            line = '%s monitor.job[%s.deploy] %s\n' % (host, tt['{#NAME}'], seq.join(tt['{#DEPLOY}']))
            lines.append(line)
            line = '%s monitor.job[%s.distributed] %s\n' % (host, tt['{#NAME}'], tt['{#DISTRIBUTED}'])
            lines.append(line)
            line = '%s monitor.job[%s.heartbeat] %s\n' % (host, tt['{#NAME}'], seq.join(tt['{#HEARTBEAT}']))
            lines.append(line)
            line = '%s monitor.job[%s.running] %s\n' % (host, tt['{#NAME}'], tt['{#RUNNING}'])
            lines.append(line)
            if True not in tt['{#RUNNING}']:
                problem = '没有运行中的定时任务: %s' % tt['{#RUNNING}']
            elif len(tt['{#DISTRIBUTED}'])>1 and False in tt['{#DISTRIBUTED}'] and tt['{#RUNNING}'].count(True)>1:
                problem = '非分布式定时任务启动了不止一个 分布式(%s) 运行状态(%s)' % (tt['{#DISTRIBUTED}'],tt['{#RUNNING}'])
            #elif len(tt['{#DISTRIBUTED}'])>1 and True in tt['{#DISTRIBUTED}'] and tt['{#RUNNING}'].count(True)!=len(tt['{#DISTRIBUTED}']):
                #problem = '分布式定时任务未全部启动 分布式(%s) 运行状态(%s)' % (tt['{#DISTRIBUTED}'],tt['{#RUNNING}'])
            else:
                problem = 'None'
            line = '%s monitor.job[%s.problem] %s\n' % (host, tt['{#NAME}'], problem)
            lines.append(line)
        fname = '/tmp/job.txt'
        f = open(fname, 'w')
        f.writelines(lines)
        f.close()
        output = commands.getoutput('zabbix_sender -z 127.0.0.1 -s monitor -i %s' % fname)
        LOG.info(output)
    elif sys.argv[3] == '--discover':
        print json.dumps(data, sort_keys=True, indent=4)
    else:
        pass
elif sys.argv[2] == 'queue':
    data = {"data": zabbix_queue.values()}
    if sys.argv[3] == '--updata':
        lines = []
        line = '%s monitor_queuebs_count %d\n' % (host, len(data['data']))
        lines.append(line)
        for tt in data['data']:
            line = '%s monitor.queue[%s.deploy] %s\n' % (host, tt['{#NAME}'], seq.join(tt['{#DEPLOY}']))
            lines.append(line)
            line = '%s monitor.queue[%s.heartbeat] %s\n' % (host, tt['{#NAME}'], seq.join(tt['{#HEARTBEAT}']))
            lines.append(line)
            line = '%s monitor.queue[%s.running] %s\n' % (host, tt['{#NAME}'], tt['{#RUNNING}'])
            lines.append(line)
            if True not in tt['{#RUNNING}']:
                problem = '没有运行中的队列监控: %s' % tt['{#RUNNING}']
            else:
                problem = 'None'
            line = '%s monitor.queue[%s.problem] %s\n' % (host, tt['{#NAME}'], problem)
            lines.append(line)
        fname = '/tmp/queue.txt'
        f = open(fname, 'w')
        f.writelines(lines)
        f.close()
        output = commands.getoutput('zabbix_sender -z 127.0.0.1 -i %s' % fname)
        LOG.info(output)
    elif sys.argv[3] == '--discover':
        print json.dumps(data, sort_keys=True, indent=4)
    else:
        pass
else:
    pass


