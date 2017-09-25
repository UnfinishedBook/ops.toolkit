#!/usr/bin/python  
# -*- coding: UTF-8 -*-

#启动本程序: ssh-agent ./http.py
#后台启动本程序: nohup ssh-agent ./http.py /mydata/maintenance/logs/ops-toolkit-http.std 2>&1 &

from gl import *
from wrap import *
from bottle import route,run

os.system('ssh-add /mydata/maintenance/identity/maintenance_rsa')
output = commands.getoutput('ssh-add -l')
if 'maintenance_rsa' not in output:
    print '请使用ssh-agent命令启动本程序,示例: \nnohup ssh-agent ./http.py /mydata/maintenance/logs/ops-toolkit-http.std 2>&1 &'
    exit()

#选择要管理的环境
env = 'test'
GL.setEnv(env)

GL.LOG = getLogger('SrvLogger', 'ops-toolkit-http.log')

intro_pro = GL.conf()[GL.project()]['intro']
intro_env = GL.deploy()[GL.env()]['intro']
intro = '进入运维工具事件循环，项目：%s，选择的环境是：%s。' % (intro_pro,intro_env)
GL.LOG.info(intro)

proj = 'quickbid-center'
ip = '10.135.17.9'
asked = False

mod = getMod(proj)
restart(mod, ip, asked)

while(True):
    s = raw_input('quit?:' )
    if s == 'y':
        break
    else:
        os.system('ssh-add -l')

network.disconnect_all()


