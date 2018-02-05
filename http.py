#!/usr/bin/python  
# -*- coding: UTF-8 -*-

#启动本程序: ssh-agent ./http.py
#后台启动本程序: nohup ssh-agent ./http.py > /mydata/maintenance/logs/ops-toolkit-http.std 2>&1 &

from gl import *
from wrap import *
from bottle import *
import pexpect
import traceback
import cherrypy
from paramiko import SSHException
import thread

f = open('/mydata/maintenance/identity/key')
pwd = f.readline()
f.close()
ch = pexpect.spawn('ssh-add /mydata/maintenance/identity/maintenance_rsa')
ch.expect('Enter passphrase for /mydata/maintenance/identity/maintenance_rsa: ')
ch.sendline(pwd)
output = commands.getoutput('ssh-add -l')
ch.close()
if 'maintenance_rsa' not in output:
    print '请使用ssh-agent命令启动本程序,示例: \nnohup ssh-agent ./http.py > /mydata/maintenance/logs/ops-toolkit-http.std 2>&1 &'
    exit()

GL.LOG = getLogger('HttpLogger', 'ops-toolkit-http.log')

def capturePkg(ip, hostip):
    cmd = 'nohup tcpdump host %s -n -nn -c 200000 > /mydata/maintenance/logs/tcpdump-%s.log 2>&1 &' % (hostip,getTimestamp())
    GL.LOG.info('抓包线程启动 : %s' % cmd)
    remoteCmd(ip, cmd, False)
    GL.LOG.info('抓包线程退出')

class MyServer(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def restart(self, env, ip, proj):
        GL.LOG.info('收到重启请求 (%s %s %s)' % (env,ip,proj))
        ret = {'err':1, 'msg':'unknown'}
        retry = 3
        GL.setEnv(env)
        if env=='pro' and GL.project()=='hp':
            hostip = '10.66.154.6'
            thread.start_new_thread(capturePkg, (ip,hostip))
        #elif env=='pro' and GL.project()=='qb':
            #hostip = 'rm-wz980pisxuvl0po6j.mysql.rds.aliyuncs.com'
            #thread.start_new_thread(capturePkg, (ip,hostip))
        while (retry != 0):
            try:
                retry -= 1
                mod = getMod(proj)
                if ip not in mod.deploy():
                    raise Exception('%s not deployed in %s on %s' % (proj,ip,env))
                asked = False   #关闭交互
                jstack = True   #重启前保存jstack的信息
                restart(mod, ip, asked, jstack)
                #remoteCmd(ip, 'ping baidu.com -c 5')
                ret['err'] = 0
                ret['msg'] = ''
                GL.LOG.info('重启操作完成 (%s %s %s)' % (env,ip,proj))
                break
            except (SystemExit,SSHException) as e:
                msg = traceback.format_exc()
                ret['err'] = 1
                ret['msg'] = msg
                GL.LOG.error('捕获到系统异常 (%s %s %s) : \n%s \n重试 %d ' % (env,ip,proj,msg,retry))
            except Exception as e:
                msg = traceback.format_exc()
                ret['err'] = 1
                ret['msg'] = msg
                GL.LOG.error('捕获到普通异常 (%s %s %s) : \n%s \n不重试' % (env,ip,proj,msg))
                retry = 0
        GL.LOG.info('本次请求处理完毕')
        return ret

conf = {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8887
       }
cherrypy.config.update(conf)
cherrypy.quickstart(MyServer())

