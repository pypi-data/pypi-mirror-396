#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import hashlib
import time
import chardet
import base64

from Crypto.Cipher import AES
#  from binascii import b2a_hex, a2b_hex

code_map = (
    'a' , 'b' , 'c' , 'd' , 'e' , 'f' , 'g' , 'h' ,
    'i' , 'j' , 'k' , 'l' , 'm' , 'n' , 'o' , 'p' ,
    'q' , 'r' , 's' , 't' , 'u' , 'v' , 'w' , 'x' ,
    'y' , 'z' , '0' , '1' , '2' , '3' , '4' , '5' ,
    '6' , '7' , '8' , '9' , 'A' , 'B' , 'C' , 'D' ,
    'E' , 'F' , 'G' , 'H' , 'I' , 'J' , 'K' , 'L' ,
    'M' , 'N' , 'O' , 'P' , 'Q' , 'R' , 'S' , 'T' ,
    'U' , 'V' , 'W' , 'X' , 'Y' , 'Z'
)

def short(long_url):
    '''生成短连接'''
    hkeys = []
    hex_text = md5(long_url)
    for i in range(0, 4):
        n = int(hex_text[i*8:(i+1)*8], 16)
        v = []
        e = 0
        for j in range(0, 5):
            x = 0x0000003D & n
            e |= ((0x00000002 & n ) >> 1) << j
            v.insert(0, code_map[x])
            n = n >> 6
        e |= n << 5
        v.insert(0, code_map[e & 0x0000003D])
        hkeys.append(''.join(v))
    return hkeys

def sha1(text):
    '''Returns a sha1 hash object; optionally initialized with a string'''
    sha1 = hashlib.sha1()
    sha1.update(text.encode())
    return sha1.hexdigest()

def sha256(text):
    '''Returns a sha256 hash object; optionally initialized with a string'''
    sha1 = hashlib.sha256()
    sha1.update(text.encode())
    return sha1.hexdigest()

def sha512(text):
    '''Returns a sha512 hash object; optionally initialized with a string'''
    sha1 = hashlib.sha512()
    sha1.update(text.encode())
    return sha1.hexdigest()

def md5(text):
    '''Returns a md5 hash object; optionally initialized with a string'''
    sha1 = hashlib.md5()
    sha1.update(text.encode())
    return sha1.hexdigest()

def md5_file(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
        return h.hexdigest()

class AESecurity():
    @classmethod
    def generate_key(cls):
        return md5('{}'.format(time.time()))

    def __init__(self, key):
        self.key = key
        self.iv = key[:16]
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        '''
        加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
        '''
        cryptor = AES.new(self.key, self.mode, self.iv)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        #  return b2a_hex(self.ciphertext).decode("utf-8")
        return base64.b64encode(self.ciphertext).decode("utf-8")

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        #  plain_text = cryptor.decrypt(a2b_hex(text)).decode("utf-8")
        plain_text = cryptor.decrypt(base64.b64decode(text)).decode("utf-8")
        return plain_text.rstrip('\x00')
