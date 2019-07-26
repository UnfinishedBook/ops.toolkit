#!/usr/bin/python  
# -*- coding: UTF-8 -*-

#启动本程序: ssh-agent ./cron.py
#后台启动本程序: nohup ssh-agent ./cron.py > /mydata/maintenance/logs/ops-toolkit-cron.std 2>&1 &
#*/1 * * * * ssh-agent /mydata/maintenance/scripts/ops.toolkit/cron.py >> /mydata/maintenance/logs/ops-toolkit-cron.std 2>&1

import os
os.environ['ops_project'] = 'hp'
os.environ['ops_key'] = 'maintenance'

from gl import *
from wrap import *
import pexpect
import traceback

#f = open('/mydata/maintenance/identity/key')
#pwd = f.readline()
#f.close()
#ch = pexpect.spawn('ssh-add /mydata/maintenance/identity/maintenance_rsa')
#ch.expect('Enter passphrase for /mydata/maintenance/identity/maintenance_rsa: ')
#ch.sendline (pwd)
#output = commands.getoutput('ssh-add -l')
#ch.close()
#if 'maintenance_rsa' not in output:
    #print '请使用ssh-agent命令启动本程序,示例: \nnohup ssh-agent ./cron.py > /mydata/maintenance/logs/ops-toolkit-cron.std 2>&1 &'
    #exit()

GL.LOG = getLogger('CronLogger', 'ops-toolkit-cron.log')

try:
    GL.LOG.info('开始')
    env = 'pro'
    proj = 'hpyp-center'
    GL.setEnv(env)
    mod = getMod(proj)
    order = 'pwd'
    for ip in mod.deploy():
        GL.LOG.info('(%s %s %s) 操作开始' % (env,ip,order))
        remoteCmd(ip, order)
        GL.LOG.info('(%s %s %s) 操作完成' % (env,ip,order))
except Exception as e:
    msg = traceback.format_exc()
    GL.LOG.error('(%s %s %s) 操作异常 \n%s' % (env,ip,order,msg))
finally:
    GL.LOG.info('结束')
    network.disconnect_all()

