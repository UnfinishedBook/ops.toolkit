#!/usr/bin/python  
# -*- coding: UTF-8 -*-

from gl import *
from wrap import *
#import rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from binascii import b2a_hex,a2b_hex

from fabric.api import env,local,cd,run,execute
from fabric.contrib.project import rsync_project

def ftest():
    #run('tempID=`ps -ef | grep quickbid-server | grep -v grep | awk \'{print $2}\'`; [ -n "$tempID" ] && kill -9 $tempID; echo ok')
    run('tmpid=`ps -ef|grep tomcat-quickbid-server|grep java|grep -v grep|awk \'{print $2}\'`; [ -n "$tmpid" ] && kill -9 $tmpid; echo ok')

if os.environ.has_key('SSH_AGENT_PID') == False:
    print '启动方式: ssh-agent ./test.py'
    exit()
f = open('/mydata/maintenance/identity/key')
pwd = f.readline()
f.close()
ch = pexpect.spawn('ssh-add /mydata/maintenance/identity/maintenance_rsa')
ch.expect('Enter passphrase for /mydata/maintenance/identity/maintenance_rsa: ')
ch.sendline (pwd)
output = commands.getoutput('ssh-add -l')
ch.close()
if 'maintenance_rsa' not in output:
    #print '需要先配置好ssh-agent: \nssh-agent bash\nssh-add /mydata/maintenance/identity/maintenance_rsa'
    print '添加ssh key到ssh-agent失败, 请检查.'
    exit()

GL.setEnv('test')
GL.LOG = getLogger('TestLogger', 'ops-toolkit-test.log')

#h = '10.104.197.116'
#h = '172.18.27.5'
#execute(ftest, host=h)

#password = getpass.getpass('请输入使用密码：')
#if verifyPwd(password) == False:
    #exit()
#GL.setPwd(password)

m1 = Model('quickbid-center')
savejstack(m1, '172.18.27.5')
#print m1.port()

#timekeeping(10)
#print 'over'

#m1 = Model('quickbid-center')
#print m1.name(),m1.form(),m1.deploy(),m1.appdir(),m1.cnfdir(),m1.bakdir()
#print m1.upappdir(),m1.pack()





