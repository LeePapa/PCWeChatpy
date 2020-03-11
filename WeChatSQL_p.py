# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 17:33:40 2020

@author: Limour
"""

from Crypto.Cipher import AES
import hashlib, hmac, ctypes

SQLITE_FILE_HEADER = bytes("SQLite format 3",encoding='ASCII') + bytes(1)#文件头
IV_SIZE = 16
HMAC_SHA1_SIZE = 20
KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096 #4048数据 + 16IV + 20 HMAC + 12
DEFAULT_ITER = 64000

password = bytes.fromhex("AA4FCC1DDD2E6EE4404BB4D0FF5523ED8D034F214426C3A33D9735D33E92BBAA")

with open(r'C:\Users\ \Documents\WeChat Files\ \Msg\ChatMsg.db', 'rb') as f:
    blist = f.read()
print(len(blist))

salt = blist[:16]#微信将文件头换成了盐
key = hashlib.pbkdf2_hmac('sha1', password, salt, DEFAULT_ITER, KEY_SIZE)#获得Key

first = blist[16:DEFAULT_PAGESIZE]#丢掉salt

# import struct
mac_salt = bytes([x^0x3a for x in salt])
mac_key = hashlib.pbkdf2_hmac('sha1', key, mac_salt, 2, KEY_SIZE)

hash_mac = hmac.new(mac_key ,digestmod = 'sha1')#用第一页的Hash测试一下
hash_mac.update(first[:-32])
hash_mac.update(bytes(ctypes.c_int(1)))
# hash_mac.update(struct.pack('=I',1))
if (hash_mac.digest() == first[-32:-12]):
    print('Correct Password')
else:
    raise RuntimeError('Wrong Password')

blist = [blist[i:i+DEFAULT_PAGESIZE] for i in range(DEFAULT_PAGESIZE,len(blist),DEFAULT_PAGESIZE)]
with open(r'E:\Works\ChatMsg.db', 'wb') as f:
    f.write(SQLITE_FILE_HEADER)#写入文件头
    t = AES.new(key ,AES.MODE_CBC ,first[-48:-32])
    f.write(t.decrypt(first[:-48]))
    f.write(first[-48:])
    for i in blist:
            t = AES.new(key ,AES.MODE_CBC ,i[-48:-32])
            f.write(t.decrypt(i[:-48]))
            f.write(i[-48:])


