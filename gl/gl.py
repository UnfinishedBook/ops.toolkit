#!/usr/bin/python  
# -*- coding: UTF-8 -*-

import sys
import os
import locale
import json
import commands
import time
import datetime
import getpass
import re
import requests
#from pexpect.pxssh import pxssh
from Crypto.Cipher import AES
from Crypto import Random
from binascii import b2a_hex,a2b_hex

#配置编码
reload(sys)
sys.setdefaultencoding('utf8')
language_code, encoding = locale.getdefaultlocale()
locale.setlocale(locale.LC_ALL, '%s.%s' % (language_code, encoding))

#issue  问题
#opt    可选的答案，逗号分隔的字符串
#df     默认的答案
def ask(issue, opt, df=None):
    lt = opt.split(',')
    if len(lt) < 2:
        return None
    if df!=None and df not in lt:
        return None

    askstr = None
    for it in lt:
        if askstr == None:
            askstr = it
        else:
            askstr = '%s or %s' % (askstr,it)
    askstr = '%s [%s] : ' % (issue,askstr)
    while True:
        instr = raw_input(askstr)
        if instr == '':
            if df == None:
                continue
            else:
                return df
        elif instr not in lt:
            continue
        else:
            return instr
    
#key    加解密时用的密钥字符串,长度不应该大于16
#txt    加密时,待加密的字符串,长度不可以大于16;解密时为待解密的字符串
#encrypt    True,加密;False,解密
def cipher(key, txt, encrypt=True):
    if len(key) > 16:
        key = key[:15]
    if len(key) < 16:
        for n in range(16-len(key)):
            key += ' '
    iv = Random.new().read(AES.block_size)
    obj = AES.new(key, AES.MODE_ECB, iv)
    if encrypt:
        if len(txt) > 16:
            txt = txt[:15]
        if len(txt) < 16:
            for n in range(16-len(txt)):
                txt += ' '
        en = obj.encrypt(txt)
        return b2a_hex(en)
    else:
        en = a2b_hex(txt)
        return obj.decrypt(en).strip()

def locadJson(jsonStr):
    return json.loads(jsonStr)

def loadJsonFile(fileName):
    return json.load(open(fileName, 'r'))

def dumpJson(pyObj):
    return json.dumps(pyObj, sort_keys=True, indent=4)

def dumpJsonFile(pyObj, fileName):
    json.dump(pyObj, open(fileName, 'w'), sort_keys=True, indent=4)

def getTimestamp():
    #return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

#def sshLogin(ip, user, pwd=None, rsa=None):
    #client = pxssh()
    #if pwd==None and rsa==None:
        #client.login(ip, user)
    #elif rsa == None:
        #client.login(ip, user, pwd)
    #elif pwd == None:
        #client.login(ip, user, ssh_key=rsa)
    #else:
        #client.login(ip, user, pwd, ssh_key=rsa)
    #return client

#def sshExecute(client, cmd):
    #client.sendline(cmd)
    #client.prompt()
    #return client.before

#def sshLogout(client):
    #client.logout()

class Global:
    def __init__(self):
        #从环境变量读取加密key和当前系统
        if os.environ.has_key('ops_key')==False or os.environ.has_key('ops_project')==False:
            print "必须先配置好环境变量(建议配置到~/.bashrc),示例: \nexport ops_key='maintenance'\nexport ops_project='qb'"
            exit()
        self.__key = os.environ['ops_key']
        self.__project = os.environ['ops_project']
        self.__dirMain = sys.path[0]    #程序的主目录
        self.__dirCfg = '%s/conf' % self.__dirMain  #配置文件目录
        self.__conf = loadJsonFile('%s/conf.json' % self.__dirCfg)
        #self.__project = self.__conf['project']
        self.__issue = self.__conf[self.__project]['issue']
        self.__pkdir = self.__conf[self.__project]['pkdir']
        self.__deploy = loadJsonFile('%s/%s/deploy.json' % (self.__dirCfg,self.__project))
        self.__form = loadJsonFile('%s/%s/form.json' % (self.__dirCfg,self.__project))
        self.__proj = loadJsonFile('%s/%s/proj.json' % (self.__dirCfg,self.__project))
        #self.__rsa ='/mydata/maintenance/identity/maintenance_rsa'
        #self.__rsa ='/root/.ssh/id_rsa'
        self.__env = None
        #self.remote = {}
        self.__monitor = None
        self.__mlogin = None
        self.__mget_job = None
        self.__mget_queue = None
        self.__mctl_job = None
        self.__mctl_queue = None
        self.__mget_center = None
        self.__mctl_center = None
        self.__muser = None
        self.__mpwd = None
        self.__closeJobs = None
        self.__closeQueues = None
        self.__svn = None
        self.__branch = None
        self.__default_proj = None
        self.LOG = None

    def dirMain(self):
        return self.__dirMain

    def dirCfg(self):
        return self.__dirCfg

    def conf(self):
        return self.__conf

    def deploy(self):
        return self.__deploy

    def form(self):
        return self.__form

    def proj(self):
        return self.__proj

    #def rsa(self):
        #return self.__rsa

    def key(self):
        return self.__key

    def env(self):
        return self.__env

    def setEnv(self, tmp):
        self.__env = tmp

    def project(self):
        return self.__project

    def issue(self):
        return self.__issue

    def setIssue(self, tmp):
        self.__issue = tmp

    def pkdir(self):
        return self.__pkdir

    def monitor(self):
        if self.__monitor == None:
            self.__monitor = self.deploy()[self.env()]['monitor']
        return self.__monitor

    def mlogin(self):
        if self.__mlogin == None:
            self.__mlogin = self.deploy()[self.env()]['mlogin']
        return self.__mlogin

    def mget_job(self):
        if self.__mget_job == None:
            self.__mget_job = self.deploy()[self.env()]['mget_job']
        return self.__mget_job

    def mget_queue(self):
        if self.__mget_queue == None:
            self.__mget_queue = self.deploy()[self.env()]['mget_queue']
        return self.__mget_queue

    def mctl_job(self):
        if self.__mctl_job == None:
            self.__mctl_job = self.deploy()[self.env()]['mctl_job']
        return self.__mctl_job

    def mctl_queue(self):
        if self.__mctl_queue == None:
            self.__mctl_queue = self.deploy()[self.env()]['mctl_queue']
        return self.__mctl_queue

    def mget_center(self):
        if self.__mget_center == None:
            self.__mget_center = self.deploy()[self.env()]['mget_center']
        return self.__mget_center

    def mctl_center(self):
        if self.__mctl_center == None:
            self.__mctl_center = self.deploy()[self.env()]['mctl_center']
        return self.__mctl_center

    def muser(self):
        if self.__muser == None:
            self.__muser = self.deploy()[self.env()]['muser']
        return self.__muser

    def mpwd(self):
        if self.__mpwd == None:
            tmp = self.deploy()[self.env()]['mpwd']
            self.__mpwd = cipher(GL.key(), tmp, False)
        return self.__mpwd

    def setCloseJobs(self, tmp):
        self.__closeJobs = tmp

    def setCloseQueues(self, tmp):
        self.__closeQueues = tmp

    def closeJobs(self):
        return self.__closeJobs

    def closeQueues(self):
        return self.__closeQueues

    def svn(self):
        if self.__svn == None:
            tmp = cipher(GL.key(), self.conf()[self.project()]['svn'], False)
            self.__svn = 'svn://%s' % tmp
        return self.__svn

    def setBranch(self, new):
        self.__branch = new

    def branch(self):
        return self.__branch

    def defaultProj(self):
        return self.__default_proj

    def setDefaultProj(self, proj):
        self.__default_proj = proj

GL = Global()


