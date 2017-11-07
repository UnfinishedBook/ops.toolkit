#!/usr/bin/python  
# -*- coding: UTF-8 -*-

from gl import *
from wrap import *
from cmd2 import Cmd
import pexpect

class Loop(Cmd):
    def __init__(self):
        self.cmdask = False
        #将变量纳入环境变量，就可以通过set命令修改和查询
        self.settable['cmdask'] = 'whether to ask when cmd is called'
        Cmd.__init__(self)

    #事件循环开始时执行
    def preloop(self):
        #验证管理密码
        #password = getpass.getpass('请输入使用密码：')
        #if verifyPwd(password) == False:
            #exit()
        #GL.setPwd(password)

        #给ssh-agent加入本程序需要的ssh key
        if os.environ.has_key('SSH_AGENT_PID') == False:
            print '启动方式: ssh-agent ./main.py'
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

        #选择要管理的环境
        env = self.select(GL.deploy().keys())
        GL.setEnv(env)
        GL.LOG = getLogger('TheLogger', 'ops-toolkit.log')

        intro_pro = GL.conf()[GL.project()]['intro']
        intro_env = GL.deploy()[GL.env()]['intro']
        self.intro = '进入运维工具事件循环，项目：%s，选择的环境是：%s。' % (intro_pro,intro_env)
        self.prompt = "运维 %s %s ->> " % (intro_pro,intro_env)

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
            item = args[0]
            drt = args[1]
            if drt.startswith("'") and drt.endswith("'"):
                drt = 'eval ' + drt
            if GL.proj().has_key(item):
                mod = getMod(item)
                if mod != None:
                    cmd(mod.deploy(), drt, self.cmdask)
            elif GL.deploy()[GL.env()]['deploy'].has_key(item):
                ip_list = [item,]
                cmd(ip_list, drt, self.cmdask)
            elif item == 'all':
                ip_list = GL.deploy()[GL.env()]['deploy'].keys()
                cmd(ip_list, drt, self.cmdask)
            else:
                self.help_cmd()
        else:
            self.help_cmd()

    def help_cmd(self):
        print '在指定工程所在主机或指定IP的主机上执行命令，用法：cmd <工程名/ip/all> <命令>'

    def do_local(self, cmd):
        if cmd!=None and cmd!='':
            if cmd.startswith("'") and cmd.endswith("'"):
                cmd = 'eval ' + cmd
            GL.LOG.info('本地执行命令：%s' % cmd)
            localCmd(cmd)

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

    def do_patch(self, proj):
        if proj!=None and proj!='':
            mod = getMod(proj)
            if mod!=None and mod.name()=='wap':
                up_wap(mod, True)
            else:
                self.help_patch()
        else:
            self.help_patch()

    def help_patch(self):
        print '更新指定的工程的补丁(当前只支持wap)，用法：patch <工程名>'

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
            else:
                self.help_svn()

    def help_svn(self):
        print '用法：svn <操作 [info/up/switch/merge/cp/del/ls/ci]> <工程名> [详细路径]'

    def do_svncnf(self, arg):
        args = arg.split(' ')
        if len(args) != 2:
            self.help_svncnf()
        else:
            mod = getMod(args[1])
            if mod!=None and (mod.form()=='center' or mod.form()=='process' or mod.form()=='server'):
                opt = args[0]
                svncnf(mod, opt)
            else:
                self.help_svncnf()

    def help_svncnf(self):
        print '用法：svncnf <操作 [up/merge/cp/del/ls/ci]> <工程名> //注意当前只有center/process/server有配置文件'

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

    def do_dubbo(self, arg):
        args = arg.split(' ', 2)
        if len(args)==2 and (args[0]=='disable' or args[0]=='enable'):
            mod = getMod(args[1])
            if mod != None:
                for ip in mod.deploy():
                    dubboAdmin(mod, ip, args[0])
        elif len(args)==3 and (args[0]=='disable' or args[0]=='enable'):
            mod = getMod(args[1])
            if mod != None:
                dubboAdmin(mod, args[2], args[0])
        else:
            self.help_dubbo()

    def help_dubbo(self):
        print '''启用/禁用DubboAdmin,只用于center工程, 用法: 
        dubbo enable/disable <工程名>
        dubbo enable/disable <工程名> <ip>'''

    def do_encrypt(self, arg):
        if arg!=None and arg!='':
            print cipher(GL.key(),arg)

    def do_decrypt(self, arg):
        if arg!=None and arg!='':
            print cipher(GL.key(),arg, False)

    def do_info(self, arg):
        if GL.proj().has_key(arg):
            mod = getMod(arg)
            if mod != None:
                print dumpJson(mod.deploy())
                print dumpJson(GL.proj()[arg])
        elif GL.deploy()[GL.env()]['deploy'].has_key(arg):
            print dumpJson(GL.deploy()[GL.env()]['deploy'][arg])
        elif arg == 'all':
            print dumpJson(GL.deploy()[GL.env()])
        else:
            pass

    def do_scp(self, arg):
        args = arg.split(' ', 2)
        if len(args) != 3:
            self.help_scp()
            return
        if (args[1].startswith(':') and args[2].startswith(':')) or (args[1].startswith(':')==False and args[2].startswith(':')==False):
            self.help_scp()
            return
        src = args[1]
        dest = args[2]
        if GL.proj().has_key(args[0]):
            mod = getMod(args[0])
            if mod != None:
                ip_list = mod.deploy()
                scp(ip_list, src, dest)
        elif GL.deploy()[GL.env()]['deploy'].has_key(args[0]):
            ip_list = [args[0],]
            scp(ip_list, src, dest)
        elif args[0] == 'all':
            ip_list = GL.deploy()[GL.env()]['deploy'].keys()
            scp(ip_list, src, dest)
        else:
            self.help_scp()
    
    def help_scp(self):
        print '''远程拷贝文件，用法：
        scp <工程名/ip/all> <src> <dest>  通过参数2得到机器，src和dest前面加:则表示为远程目录，有且只有一个为远程目录
        '''

    def do_rsync(self, arg):
        args = arg.split(' ', 2)
        if len(args) != 3:
            self.help_rsync()
            return
        if (args[1].startswith(':') and args[2].startswith(':')) or (args[1].startswith(':')==False and args[2].startswith(':')==False):
            self.help_rsync()
            return
        src = args[1]
        dest = args[2]
        if GL.proj().has_key(args[0]):
            mod = getMod(args[0])
            if mod != None:
                ip_list = mod.deploy()
                rsync(ip_list, src, dest)
        elif GL.deploy()[GL.env()]['deploy'].has_key(args[0]):
            ip_list = [args[0],]
            rsync(ip_list, src, dest)
        elif args[0] == 'all':
            ip_list = GL.deploy()[GL.env()]['deploy'].keys()
            rsync(ip_list, src, dest)
        else:
            self.help_rsync()
    
    def help_rsync(self):
        print '''远程同步目录，用法：
        rsync <工程名/ip/all> <src> <dest>  通过参数2得到机器，src和dest前面加:则表示为远程目录，有且只有一个为远程目录
        '''

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
        






