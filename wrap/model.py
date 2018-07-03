#!/usr/bin/python  
# -*- coding: UTF-8 -*-

from gl import *

class Model:
    def __init__(self, name):
        self.__name = name
        self.__form = GL.proj()[name]['form']
        self.__deploy = []
        self.__appdir = None
        self.__upappdir = None
        self.__cnfdir = None
        self.__bakdir = None
        self.__pack = None
        self.__trunk = None
        self.__tag = None
        self.__workcopy = None
        self.__trunk_cnf = None
        self.__tag_cnf = None
        self.__workcopy_cnf = None
        self.__gcdir = None
        self.__gcbakdir = None
        self.__port = None
        self.__jstackdir = None
        self.__issue = None

    def name(self):
        return self.__name

    def form(self):
        return self.__form

    def tomcat(self):
        return GL.proj()[self.name()]['tomcat']

    def deploy(self):
        if len(self.__deploy) == 0:
            ips = GL.deploy()[GL.env()]['deploy']
            for ip in ips:
                for t in ips[ip]:
                    if t == self.name():
                        self.__deploy.append(ip)
        return self.__deploy

    def appdir(self):   #应用部署目录
        if self.__appdir == None:
            tmp = GL.proj()[self.name()]['appdir']
            if tmp.startswith('/'): #绝对路径,就直接使用
                self.__appdir = tmp
            else:   #相对路径,就要加上form中的appdir
                if self.form()=='server' or self.form()=='module':
                    tmp = '%s/%s' % (self.tomcat(),tmp)
                self.__appdir = '%s/%s' % (GL.form()[self.form()]['appdir'],tmp)
        return self.__appdir

    def upappdir(self): #应用部署的上层目录
        if self.__upappdir == None:
            self.__upappdir = self.appdir()[:self.appdir().rfind('/')]
        return self.__upappdir

    def cnfdir(self):   #配置文件目录
        if self.__cnfdir == None:
            self.__cnfdir = '%s/%s' % (GL.form()[self.form()]['cnfdir'],self.name())
        return self.__cnfdir

    def gcdir(self):    #gc日志目录
        if self.__gcdir == None:
            self.__gcdir = '%s/gc/%s/%s' % (GL.form()['logdir'],self.form(),self.name())
        return self.__gcdir

    def gcbakdir(self):    #gc日志的备份目录
        if self.__gcbakdir == None:
            self.__gcbakdir = '%s/logs/gc/%s/%s' % (GL.form()['bakdir'],self.form(),self.name())
        return self.__gcbakdir

    def jstackdir(self):    #jstack信息的保存目录
        if self.__jstackdir == None:
            self.__jstackdir = '%s/logs/jstack/%s/%s' % (GL.form()['bakdir'],self.form(),self.name())
        return self.__jstackdir

    def bakdir(self):   #备份目录
        if self.__bakdir == None:
            self.__bakdir = GL.form()['bakdir']
        return self.__bakdir

    def port(self):
        if self.__port== None:
            self.__port = GL.proj()[self.name()]['port']
        return self.__port

    def pack(self):   #更新包
        if self.__pack == None:
            tmp = GL.proj()[self.name()]['pack']
            if tmp.startswith('/'): #绝对路径,就直接使用
                self.__pack = tmp
            else:   #相对路径,就要加上form中的updir
                self.__pack = '%s/%s' % (GL.form()[self.form()]['updir'],tmp)
        return self.__pack

    def pidname(self):  #查询进程时用的字符串
        if self.form()=='server' or self.form()=='module':
            return '/%s/' % self.tomcat()
        elif self.form()=='center' or self.form()=='process' or self.form()=='newserver':
            return self.appdir() + '/'
        else:
            return None

    def tomcatshutdown(self):
        if self.form()=='server' or self.form()=='module':
            return '%s/%s/bin/shutdown.sh' % (GL.form()[self.form()]['appdir'],self.tomcat())
        else:
            return None

    def pidexe(self):   #启动文件
        if self.form()=='server' or self.form()=='module':
            return '%s/%s/bin/startup.sh' % (GL.form()[self.form()]['appdir'],self.tomcat())
        elif self.form()=='center' or self.form()=='process' or self.form()=='newserver':
            if GL.env()!='pro' and self.form()=='center':
                return '%s/bin/start-dev.sh' % self.appdir()
            if GL.env()!='pro' and self.form()=='process':
                return '%s/bin/lowstart.sh' % self.appdir()
            if GL.env()!='pro' and self.form()=='newserver':
                return '%s/bin/start-dev.sh' % self.appdir()
            else:
                return '%s/bin/start.sh' % self.appdir()
        else:
            return None

    def svnsuf(self):
        return GL.proj()[self.name()]['svnsuf']

    def trunk(self):
        if self.__trunk == None:
            if GL.env() == 'pro':
                #由于当前是从测试分支合并到生产tag进行发版，所以这里的trunk是获取测试分支
                self.__trunk = '%s/%s/%s' % (GL.svn(),GL.form()['test.branch'].replace('{issue}', self.issue()),self.svnsuf())
            elif GL.env() == 'test':
                if GL.branch():
                    #从分支合并而不是主干，所以这里的trunk是获取分支路径
                    self.__trunk = '%s/%s/%s' % (GL.svn(),GL.form()['branch'].replace('{issue}', self.issue()),self.svnsuf())
                else:
                    #从主干合并
                    self.__trunk = '%s/%s/%s' % (GL.svn(),GL.form()['trunk'],self.svnsuf())
        return self.__trunk

    def tag(self):
        if self.__tag == None:
            if GL.env() == 'test':
                self.__tag = '%s/%s/%s' % (GL.svn(),GL.form()['test.branch'].replace('{issue}', self.issue()),self.svnsuf())
            elif GL.env() == 'pro':
                self.__tag = '%s/%s/%s' % (GL.svn(),GL.form()['tag'].replace('{issue}', self.issue()),self.svnsuf())
        return self.__tag

    def workcopy(self):
        if self.__workcopy == None:
            if GL.env() == 'test':
                self.__workcopy = '%s/%s' % (GL.form()['test.wcopy'].replace('{issue}', self.issue()),self.svnsuf())
            elif GL.env() == 'pro':
                self.__workcopy = '%s/%s' % (GL.form()['wcopy'].replace('{issue}', self.issue()),self.svnsuf())
        return self.__workcopy

    def cnfsuf(self):
        return GL.proj()[self.name()]['cnfsuf']

    def trunk_cnf(self):
        if self.__trunk_cnf == None:
            if GL.env() == 'pro':
                #由于当前是从测试分支合并到生产tag进行发版，所以这里的trunk是获取测试分支
                self.__trunk_cnf = '%s/%s/%s' % (GL.svn(),GL.form()['test.branch'].replace('{issue}', self.issue()),self.cnfsuf())
            elif GL.env() == 'test':
                if GL.branch():
                    #从分支合并而不是主干，所以这里的trunk是获取分支路径
                    self.__trunk_cnf = '%s/%s/%s' % (GL.svn(),GL.form()['branch'].replace('{issue}', self.issue()),self.cnfsuf())
                else:
                    #从主干合并
                    self.__trunk_cnf = '%s/%s/%s' % (GL.svn(),GL.form()['trunk'],self.cnfsuf())
        return self.__trunk_cnf

    def tag_cnf(self):
        if self.__tag_cnf == None:
            if GL.env() == 'test':
                self.__tag_cnf = '%s/%s/%s' % (GL.svn(),GL.form()['test.branch'].replace('{issue}', self.issue()),self.cnfsuf())
            elif GL.env() == 'pro':
                self.__tag_cnf = '%s/%s/%s' % (GL.svn(),GL.form()['tag'].replace('{issue}', self.issue()),self.cnfsuf())
        return self.__tag_cnf

    def workcopy_cnf(self):
        if self.__workcopy_cnf == None:
            if GL.env() == 'test':
                self.__workcopy_cnf = '%s/%s' % (GL.form()['test.wcopy'].replace('{issue}', self.issue()),self.cnfsuf())
            elif GL.env() == 'pro':
                self.__workcopy_cnf = '%s/%s' % (GL.form()['wcopy'].replace('{issue}', self.issue()),self.cnfsuf())
        return self.__workcopy_cnf

    def issue(self):
        if self.__issue != None:
            return self.__issue
        elif GL.proj()[self.name()].has_key('issue'):
            self.__issue = GL.proj()[self.name()]['issue']
            return self.__issue
        else:
            return GL.issue()

#根据工程名获得一个Model实例
def getMod(proj):
    if proj == '!$':
        proj = GL.defaultProj()
    if GL.proj().has_key(proj):
        GL.setDefaultProj(proj)
        return Model(proj)
    else:
        print '未发现 (%s/%s) 的部署信息' % (GL.env(),proj)
        return None



