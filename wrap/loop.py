#!/usr/bin/python  
# -*- coding: UTF-8 -*-

from gl import *
from wrap import *
from cmd2 import Cmd

class Loop(Cmd):
    def __init__(self):
        Cmd.__init__(self)

    #事件循环开始时执行
    def preloop(self):
        #验证管理密码
        #password = getpass.getpass('请输入使用密码：')
        #if verifyPwd(password) == False:
            #exit()
        #GL.setPwd(password)

        #验证ssh-agent
        output = commands.getoutput('ssh-add -l')
        if 'maintenance_rsa' not in output:
            print '必须先配置好ssh-agent: \nssh-agent bash\nssh-add /mydata/maintenance/identity/maintenance_rsa'
            exit()

        #选择要管理的环境
        env = self.select(GL.deploy().keys())
        GL.setEnv(env)

        intro = GL.deploy()[GL.env()]['intro']
        if GL.project() == 'quickbid':
            project = '闪拍'
        elif GL.project() == 'duobao':
            project = '夺宝'
        else:
            LOG.error('不支持的项目 %s' % GL.project())
            exit()
        self.intro = '进入运维工具事件循环，项目：%s，选择的环境是：%s。' % (project,intro)
        self.prompt = "运维 %s %s ->> " % (project,intro)

    #事件循环结束时执行
    def postloop(self):
        #for ip,remote in GL.remote.items():
            #remote.logout()
        network.disconnect_all()

    #输入为空时啥都不做
    def emptyline(self):
        return

    #exit指令，当指令返回是True时事件循环结束
    def do_exit(self, arg):
        return True

    #自定义指令中默认的自动补全内容
    def completedefault(self, text, line, begidx, endidx):
        projs = GL.proj().keys()
        if text==None or text=='':
            return projs
        else:
            ret = []
            for proj in projs:
                if proj.startswith(text):
                    ret.append(proj)
        return ret

    def do_cmd(self, arg):
        args = arg.split(' ', 1)
        if len(args) == 2:
            if GL.proj().has_key(args[0]):
                mod = getMod(args[0])
                if mod != None:
                    cmd_mod(mod, args[1])
            elif GL.deploy()[GL.env()]['deploy'].has_key(args[0]):
                cmd_ip(args[0], args[1])
            elif args[0] == 'all':
                cmd_all(args[1])
            else:
                pass
        else:
            self.help_cmd()

    def help_cmd(self):
        print '在指定工程所在主机执行命令，用法：cmd <工程名> <命令>'

    def do_backup(self, proj):
        if proj!=None and proj!='':
            mod = getMod(proj)
            if mod != None:
                backup(mod)
        else:
            self.help_backup()

    def help_backup(self):
        print '备份指定的工程，用法：backup <工程名>'

    def do_up(self, proj):
        if proj!=None and proj!='':
            mod = getMod(proj)
            if mod!=None and mod.form()!='node':
                update(mod)
            else:
                self.help_up()
        else:
            self.help_up()

    def help_up(self):
        print '更新指定的工程(node请使用svn更新)，用法：up <工程名>'

    def do_svn(self, arg):
        args = arg.split(' ')
        if len(args)!=2 and len(args)!=3:
            self.help_svn()
        else:
            mod = getMod(args[1])
            if mod != None:
                opt = args[0]
                if len(args) == 2:
                    svn(mod, opt)
                if len(args) == 3:
                    svn(mod, opt, args[2])

    def help_svn(self):
        print '用法：svn <操作 [info/up/switch/merge/ci]> <工程名> [详细路径]'

    def do_start(self, proj):
        if proj!=None and proj!='':
            mod = getMod(proj)
            if mod!=None and mod.form()!='node':
                start(mod)
            else:
                self.help_start()
        else:
            self.help_start()

    def help_start(self):
        print '启动Java工程，用法：start <工程名>'

    def do_stop(self, proj):
        if proj!=None and proj!='':
            mod = getMod(proj)
            if mod!=None and mod.form()!='node':
                stop(mod)
            else:
                self.help_stop()
        else:
            self.help_stop()

    def help_stop(self):
        print '停止Java工程，用法：stop <工程名>'

    def do_restart(self, proj):
        if proj!=None and proj!='':
            mod = getMod(proj)
            if mod!=None and mod.form()!='node':
                restart(mod)
            else:
                self.help_restart()
        else:
            self.help_restart()

    def help_restart(self):
        print '重启Java工程(node请使用pm2 reload)，用法：restart <工程名>'

    def do_pm2(self, arg):
        if arg=='l' or arg=='list':
            pm2(arg)
        else:
            args = arg.split(' ', 1)
            if len(args)==2 and args[0]=='reload':
                mod = getMod(args[1])
                if mod!=None and mod.form()=='node':
                    pm2(args[0], mod)
                else:
                    self.help_pm2()
            else:
                self.help_pm2()

    def help_pm2(self):
        print '''操作node工程的pm2命令，用法：
        pm2 <l/list>        
        pm2 reload <工程名>'''


    def do_status(self, proj):
        if proj!=None and proj!='':
            mod = getMod(proj)
            if mod!=None and mod.form()!='node':
                status(mod)
            else:
                self.help_status()
        else:
            self.help_status()

    def help_status(self):
        print '查询指定Java工程的进程情况，用法：status <工程名>'

    def do_monitor(self, arg):
        args = arg.split(' ', 2)
        if len(args)==1 and args[0]=='save':
            monitorSave()
        elif len(args)==2 and (args[0]=='show' or args[0]=='save' or args[0]=='close' or args[0]=='start'):
            mod = getMod(args[1])
            if mod != None:
                monitor(args[0], mod)
        else:
            self.help_monitor()

    def help_monitor(self):
        print '''控制工程的定时任务和队列监控，用法：
        monitor save                    显示当前save的jobs和queues
        monitor save <工程名>           保存指定工程的jobs和queues
        monitor show <工程名>           显示指定工程的jobs和queues，和它们的运行状态
        monitor <start/close> <工程名>  开启/关闭已save中对应工程的jobs和queues'''

    def do_encrypt(self, arg):
        if arg!=None and arg!='':
            print cipher(GL.key(),arg)

    def do_decrypt(self, arg):
        if arg!=None and arg!='':
            print cipher(GL.key(),arg, False)

    #def do_set(self, arg):
        #args = arg.split(' ')
        #if len(args)==1 and arg=='show':
            #set(arg)
        #elif len(args) == 2:
            #set(args[0], args[1])
        #else:
            #self.help_set()
##
    #def help_set(self):
        #print '设置变量，当前只支持版本变量issue，用法：set <show/变量> [变量值]'
        






