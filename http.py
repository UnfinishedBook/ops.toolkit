#!/usr/bin/python  
# -*- coding: UTF-8 -*-

#启动本程序: ssh-agent ./http.py
#后台启动本程序: nohup ssh-agent ./http.py /mydata/maintenance/logs/ops-toolkit-http.std 2>&1 &

from gl import *
from wrap import *
from bottle import *

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

@error(404)
def error404(error):
    return 'Nothing here, sorry\n'

@route('/restart', method='POST')
def http_restart():
    try:
        ret = {'err':0, 'msg':''}
        keys = request.params.keys()
        proj = request.params.get('proj')
        ip = request.params.get('ip')
        mod = getMod(proj)
        if ip not in mod.deploy():
            raise Exception('%s not deployed in %s' % (proj,ip))
        asked = False
        restart(mod, ip, asked)
        return ret
    except Exception,e:
        ret['err'] = 1
        ret['msg'] = str(e)
        return ret

run(host='0.0.0.0', port=8887, debug=True)
network.disconnect_all()


