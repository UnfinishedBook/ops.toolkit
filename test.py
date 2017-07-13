#!/usr/bin/python  
# -*- coding: UTF-8 -*-

from gl import *
from wrap import *
#import rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from binascii import b2a_hex,a2b_hex

GL.setEnv('test')
password = getpass.getpass('请输入使用密码：')
if verifyPwd(password) == False:
    exit()
GL.setPwd(password)

m1 = Model('qbpay-server')
print m1.deploy()

#m1 = Model('quickbid-center')
#print m1.name(),m1.form(),m1.deploy(),m1.appdir(),m1.cnfdir(),m1.bakdir()
#print m1.upappdir(),m1.pack()





