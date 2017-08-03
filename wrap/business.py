#!/usr/bin/python  
# -*- coding: UTF-8 -*-

from base import *
from model import *

def cmd(ip_list, cmd):
    for ip in ip_list:
        remoteCmd(ip, cmd)

def scp(ip_list, src, dest):
    for ip in ip_list:
        if src.startswith(':'):
            cmd = 'scp -r root@%s%s %s' % (ip,src,dest)
            localCmd(cmd)
        elif dest.startswith(':'):
            cmd = 'scp -r %s root@%s%s' % (src,ip,dest)
            localCmd(cmd)
        else:
            pass

def rsync(ip_list, src, dest):
    if src.endswith('/') == False:
        src += '/'
    if dest.endswith('/') == False:
        dest += '/'
    for ip in ip_list:
        if src.startswith(':'):
            cmd = 'rsync -avz root@%s%s %s' % (ip,src,dest)
            localCmd(cmd)
        elif dest.startswith(':'):
            cmd = 'rsync -avz %s root@%s%s' % (src,ip,dest)
            localCmd(cmd)
        else:
            pass

def backup(mod):
    for ip in mod.deploy():
        if mod.form() == 'server':
            src = mod.appdir() + '.war'
        else:
            src = mod.appdir()
        dest = mod.bakdir()
        srcDir = src[:src.rfind('/')]   #源文件(夹)所在路径
        name = src[src.rfind('/')+1:]   #源文件(夹)名称
        bakname = '%s-%s.tar' % (mod.name(),getTimestamp())   #备份文件的名字
        LOG.info('backup %s to %s/%s' % (src,dest,bakname))
        cmd = 'tar -cf %s/%s -C %s %s' % (dest,bakname,srcDir,name)
        if mod.name() == 'cdn':
            cmd += ' --exclude=apks'
        remoteCmd(ip, cmd)

def up_wap(mod):
    pk = '%s/wap.tar.gz' % GL.pkdir()
    if os.path.exists(pk) == False:
        print '未发现更新包：%s' % pk
        return
    src = '%s/wap' % GL.pkdir()
    if os.path.exists(src):
        cmd = 'rm -rf %s/*' % src
        LOG.debug('清理wap旧的更新临时目录，执行命令 (%s)' % cmd)
        localCmd(cmd)
    else:
        localCmd('mkdir -p %s' % src)
    cmd = 'tar -zxf %s -C %s' % (pk,src)
    LOG.debug('解压wap的更新包，执行命令 (%s)' % cmd)
    localCmd(cmd)
    if GL.env() == 'pro':
        src = '%s/prod' % src
    elif GL.env() == 'test':
        src = '%s/test' % src
    else:
        print '该环境(%s)暂不支持wap的更新' % GL.env()
        return
    if os.path.exists(src) == False:
        print '更新包与环境不匹配'
        return
    for ip in mod.deploy():
        cmd = 'rsync -azv %s/ root@%s:%s/' % (src,ip,mod.appdir())
        out = ask('将在 (%s) 运行命令 (%s), 确认立刻执行吗？' % (ip,cmd), 'yes,no', 'no')
        if out == 'yes':
            remoteCmd(ip, cmd)

def up_wap_cdn(mod):
    if GL.env() == 'pro':
        src_wap = '%s/wap/prod' % GL.pkdir()
    elif GL.env() == 'test':
        src_wap = '%s/wap/test' % GL.pkdir()
    else:
        print '该环境(%s)暂不支持wap_cdn的更新' % GL.env()
        return
    if os.path.exists(src_wap) == False:
        print '%s不存在' % src_wap
        return
    for ip in mod.deploy():
        cmdlist = [
            'rsync -azv %s/js/ root@%s:%s/js/' % (src_wap,ip,mod.appdir()),
            'rsync -azv %s/css/ root@%s:%s/css/' % (src_wap,ip,mod.appdir()),
            'rsync -azv %s/images/ root@%s:%s/images/' % (src_wap,ip,mod.appdir()),
            'rsync -azv %s/fonts/ root@%s:%s/fonts/' % (src_wap,ip,mod.appdir())
        ]
        for cmd in cmdlist:
            out = ask('将在 (%s) 运行命令 (%s), 确认立刻执行吗？' % (ip,cmd), 'yes,no', 'no')
            if out == 'yes':
                remoteCmd(ip, cmd)

def up_server(mod):
    for ip in mod.deploy():
        cmd = 'rm -rf %s*; cp %s %s' % (mod.appdir(),mod.pack(),mod.upappdir())
        out = ask('将在 (%s) 运行命令 (%s), 确认立刻执行吗？' % (ip,cmd), 'yes,no', 'no')
        if out == 'yes':
            remoteCmd(ip, cmd)

def up_center(mod):
    for ip in mod.deploy():
        cmd = 'rm -rf %s; unzip %s -d %s' % (mod.appdir(),mod.pack(),mod.upappdir())
        out = ask('将在 (%s) 运行命令 (%s), 确认立刻执行吗？' % (ip,cmd), 'yes,no', 'no')
        if out == 'yes':
            remoteCmd(ip, cmd)

def up_process(mod):
    up_center(mod)

def update(mod):
    if mod.name() == 'wap':
        up_wap(mod)
    elif mod.name() == 'wap_cdn':
        up_wap_cdn(mod)
    elif mod.form() == 'center':
        up_center(mod)
    elif mod.form() == 'process':
        up_process(mod)
    elif mod.form() == 'server':
        up_server(mod)
    else:
        LOG.error('不支持的更新: %s %s' % (mod.form(),mod.name()))

def svn(mod, opt, path=None):
    if opt!='info' and opt!='up' and opt!='merge' and opt!='ci' and opt!='switch':
        print '不支持的操作 %s' % opt
        return
    if (opt=='info' or opt=='up') and mod.form()=='node':
        if path == None:
            dest = mod.appdir()
        else:
            dest = '%s/%s' % (mod.appdir(),path)
        cmd = 'svn %s %s' % (opt,dest)
        for ip in mod.deploy():
            if opt == 'up':
                out = ask('将在 (%s) 运行命令 (%s), 确认立刻执行吗？' % (ip,cmd), 'yes,no', 'no')
                if out == 'yes':
                    remoteCmd(ip, cmd)
            else:
                remoteCmd(ip, cmd)
    elif opt == 'merge':
        #先更新本地拷贝
        cmd = 'svn up %s' % mod.workcopy()
        LOG.debug('更新本地的工作拷贝，执行命令 (%s)' % cmd)
        localCmd(cmd)
        #svn路径信息
        if path == None:
            tag = mod.tag()
            trunk = mod.trunk()
            wcopy = mod.workcopy()
        else:
            tag = '%s/%s' % (mod.tag(),path)
            trunk = '%s/%s' % (mod.trunk(),path)
            wcopy = '%s/%s' % (mod.workcopy(),path)
        #执行合并测试
        cmd = 'svn merge --dry-run %s %s %s' % (tag,trunk,wcopy)
        #LOG.debug('合并测试，执行命令 (%s)' % cmd)
        localCmd(cmd)
        #合并
        out = ask('查看合并测试结果后，请确认是否执行实际的合并操作？', 'yes,no', 'no')
        if out == 'yes':
            cmd = 'svn merge %s %s %s' % (tag,trunk,wcopy)
            LOG.debug('执行实际的合并操作 (%s)' % cmd)
            localCmd(cmd)
    elif opt == 'ci':
        if path == None:
            wcopy = mod.workcopy()
        else:
            wcopy = '%s/%s' % (mod.workcopy(),path)
        instr = raw_input('确认提交请输入提交日志，否则请直接回车: ')
        if instr != '':
            cmd = 'svn ci %s -m "%s"' % (wcopy, instr)
            LOG.debug('执行提交操作 (%s)' % cmd)
            localCmd(cmd)
    elif opt == 'switch':
        dest = mod.appdir()
        if path==None or path.startswith('svn')==False:
            print 'switch的目标必须是svn形式的url'
        else:
            cmd = 'svn switch %s %s' % (path,dest)
            for ip in mod.deploy():
                out = ask('将在 (%s) 运行命令 (%s), 确认立刻执行吗？' % (ip,cmd), 'yes,no', 'no')
                if out == 'yes':
                    remoteCmd(ip, cmd)

def status(mod):
    for ip in mod.deploy():
        cmd = "ps -ef|grep java|grep %s|grep -v grep" % mod.pidname()
        remoteCmd(ip, cmd)

def _stop(ip, mod):
    if mod.form() == 'server':
        remoteCmd(ip, mod.tomcatshutdown())
        time.sleep(2)
    #cmd = "ps -ef|grep java|grep %s|awk '{print $2}'|xargs kill -9" % mod.pidname()
    cmd = 'tmpid=`ps -ef|grep java|grep %s|grep -v grep|awk \'{print $2}\'`; [ -n "$tmpid" ] && kill -9 $tmpid; echo killed' % mod.pidname()
    remoteCmd(ip, cmd)

def _start(ip, mod):
    remoteCmd(ip, mod.pidexe(), False)

def start(mod):
    for ip in mod.deploy():
        _start(ip, mod)

def stop(mod):
    for ip in mod.deploy():
        _stop(ip, mod)

def restart(mod):
    for ip in mod.deploy():
        out = ask('将在 (%s) 重启 (%s), 确认立刻执行吗？' % (ip,mod.name()), 'yes,no', 'no')
        if out == 'yes':
            _stop(ip, mod)
            time.sleep(2)
            _start(ip, mod)

def pm2(opt, mod=None):
    if opt=='l' or opt=='list':
        mod = getMod('cms')  #以cms来定位node所在的主机
        for ip in mod.deploy():
            remoteCmd(ip, 'pm2 l')
    elif opt=='reload' and mod!=None:
        cmd = 'pm2 reload %s' % mod.name()
        for ip in mod.deploy():
            out = ask('将在 (%s) 运行命令 (%s), 确认立刻执行吗？' % (ip,cmd), 'yes,no', 'no')
            if out == 'yes':
                remoteCmd(ip, cmd)

def getMonitor(s, mod):
    jobs = None
    queues = None
    url = 'http://%s/ljob_controller/get_online_ljobs' % GL.monitor()
    r = s.post(url)
    jobs = parseJobs(r.text)
    url = 'http://%s/lqueue_controller/get_online_lqueues.do' % GL.monitor()
    r = s.post(url)
    queues = parseQueues(r.text)
    retJobs = []
    retQueues = []
    if jobs != None:
        for job in jobs:
            if job[1] == mod.name():
                retJobs.append(job)
    if queues != None:
        for q in queues:
            if q[1] == mod.name():
                retQueues.append(q)
    return (retJobs,retQueues)

def monitorJob(s, ip_id, ljobKey, start):
    url = 'http://%s/ljob_controller/send_ljob_status_request' % GL.monitor()
    if start == True:
        status = '1'
    else:
        status = '0'
    data = {'ljobKey':ljobKey,'ip':ip_id,'status':status}
    r = s.post(url, data=data)
    if r.status_code == 200:
        print 'OK'
    else:
        print '失败'

def monitorQueue(s, ip_id, lqueueKey, start):
    url = 'http://%s/lqueue_controller/send_lqueue_status_request.do' % GL.monitor()
    if start == True:
        status = '1'
    else:
        status = '0'
    data = {'lqueueKey':lqueueKey,'ip':ip_id,'status':status}
    r = s.post(url, data=data)
    if r.status_code == 200:
        print 'OK'
    else:
        print '失败'

def monitorSave():
    i = 1
    print '定时任务：'
    if GL.closeJobs() != None:
        for job in GL.closeJobs():
            print i,job[0],job[1],job[2]
            i += 1
    i = 1
    print '队列监控：'
    if GL.closeQueues() != None:
        for q in GL.closeQueues():
            print i,q[0],q[1],q[2]
            i += 1

def monitor(opt, mod):
    s = requests.session()
    url = 'http://%s/login_controller/do_login' % GL.monitor()
    r = s.post(url, data={'loginName':GL.muser(),'password':GL.mpwd()})
    if '退出登录' not in r.text:
        LOG.error('登录失败')
        return
    if opt=='show' or opt=='save':
        (jobs,queues) = getMonitor(s, mod)
        tmp1 = []
        tmp2 = []
        i = 1
        print '定时任务：'
        for job in jobs:
            print i,job[0],job[1],job[2],job[6]
            i += 1
            tmp1.append(job)
        i = 1
        print '队列监控：'
        for q in queues:
            print i,q[0],q[1],q[2],q[4]
            i += 1
            tmp2.append(q)
        if opt == 'save':
            GL.setCloseJobs(tmp1)
            GL.setCloseQueues(tmp2)
    elif opt=='start' or opt=='close':
        jobs = GL.closeJobs()
        queues = GL.closeQueues()
        if opt == 'start':
            info = '开启'
            status = True
        else:
            info = '关闭'
            status = False
        i = 1
        print '定时任务：'
        for job in jobs:
            if job[1] == mod.name():
                ip_id = job[0]
                ljobKey = '%s_%s' % (job[1],job[2])
                print i,info,ip_id,ljobKey,
                i += 1
                monitorJob(s, ip_id, ljobKey, status)
        i = 1
        print '队列监控：'
        for q in queues:
            if q[1] == mod.name():
                ip_id = q[0]
                lqueueKey = '%s_%s' % (q[1],q[2])
                print i,info,ip_id,lqueueKey,
                i += 1
                monitorQueue(s, ip_id, lqueueKey, status)

def set(var, val=None):
    if var == 'show':
        print 'issue : %s' % GL.issue()
    elif var == 'issue':
        GL.setIssue(val)








