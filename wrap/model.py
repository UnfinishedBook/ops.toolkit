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

    def bakdir(self):   #备份目录
        if self.__bakdir == None:
            self.__bakdir = GL.form()['bakdir']
        return self.__bakdir

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
        elif self.form()=='center' or self.form()=='process':
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
        elif self.form()=='center' or self.form()=='process':
            if GL.env()!='pro' and self.form()=='center':
                return '%s/bin/start-dev.sh' % self.appdir()
            if GL.env()!='pro' and self.form()=='process':
                return '%s/bin/lowstart.sh' % self.appdir()
            else:
                return '%s/bin/start.sh' % self.appdir()
        else:
            return None

    def trunk(self):
        if self.__trunk == None:
            self.__trunk = '%s/%s' % (GL.svn(),GL.proj()[self.name()]['trunk'])
        return self.__trunk

    def tag(self):
        if self.__tag == None:
            print GL.svn()
            self.__tag = '%s/%s' % (GL.svn(),GL.proj()[self.name()]['tag'].replace('{issue}', GL.issue()))
        return self.__tag

    def workcopy(self):
        if self.__workcopy == None:
            self.__workcopy = GL.proj()[self.name()]['wcopy'].replace('{issue}', GL.issue())
        return self.__workcopy


#根据工程名获得一个Model实例
def getMod(proj):
    if GL.proj().has_key(proj):
        return Model(proj)
    else:
        print '未发现 (%s/%s) 的部署信息' % (GL.env(),proj)
        return None



