#!/usr/bin/python  
# -*- coding: UTF-8 -*-

#启动本程序: ssh-agent ./http.py
#后台启动本程序: nohup ssh-agent ./http.py > /mydata/maintenance/logs/ops-toolkit-http.std 2>&1 &

from gl import *
from wrap import *
from bottle import *
import pexpect
import traceback

f = open('/mydata/maintenance/identity/key')
pwd = f.readline()
f.close()
ch = pexpect.spawn('ssh-add /mydata/maintenance/identity/maintenance_rsa')
ch.expect('Enter passphrase for /mydata/maintenance/identity/maintenance_rsa: ')
ch.sendline (pwd)
output = commands.getoutput('ssh-add -l')
ch.close()
if 'maintenance_rsa' not in output:
    print '请使用ssh-agent命令启动本程序,示例: \nnohup ssh-agent ./http.py > /mydata/maintenance/logs/ops-toolkit-http.std 2>&1 &'
    exit()

GL.LOG = getLogger('HttpLogger', 'ops-toolkit-http.log')

@error(404)
def error404(error):
    return 'Nothing here, sorry\n'

@route('/restart', method='POST')
def http_restart():
    try:
        ret = {'err':0, 'msg':''}
        keys = request.params.keys()
        env = request.params.get('env')
        ip = request.params.get('ip')
        proj = request.params.get('proj')
        GL.LOG.info('收到重启请求 (%s %s %s)' % (env,ip,proj))
        GL.setEnv(env)
        mod = getMod(proj)
        if ip not in mod.deploy():
            raise Exception('%s not deployed in %s on %s' % (proj,ip,env))
        asked = False   #关闭交互
        jstack = True   #重启前保存jstack的信息
        restart(mod, ip, asked, jstack)
        #remoteCmd(ip, 'whoami')
        GL.LOG.info('重启操作完成 (%s %s %s)' % (env,ip,proj))
        return ret
    except Exception as e:
        msg = traceback.format_exc()
        ret['err'] = 1
        ret['msg'] = msg
        GL.LOG.error('重启操作异常 (%s %s %s) : \n%s' % (env,ip,proj,msg))
        return ret
    finally:
        GL.LOG.info('重启 finally')
        network.disconnect_all()

run(host='0.0.0.0', port=8887, debug=True)


