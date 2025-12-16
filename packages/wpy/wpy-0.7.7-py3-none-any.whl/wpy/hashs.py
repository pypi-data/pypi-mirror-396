#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import hashlib
from typing import (
    List
)

__all__ = ['md5', 'md5file', 'sha1', 'sha256', 'sha512', 'short']

code_map = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
    'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
    'y', 'z', '0', '1', '2', '3', '4', '5',
    '6', '7', '8', '9', 'A', 'B', 'C', 'D',
    'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
)


def short(long_url: str) -> List[str]:
    '''生成短连接'''
    hkeys = []
    hex_text = md5(long_url)
    for i in range(0, 4):
        n = int(hex_text[i*8:(i+1)*8], 16)
        v = []
        e = 0
        for j in range(0, 5):
            x = 0x0000003D & n
            e |= ((0x00000002 & n) >> 1) << j
            v.insert(0, code_map[x])
            n = n >> 6
        e |= n << 5
        v.insert(0, code_map[e & 0x0000003D])
        hkeys.append(''.join(v))
    return hkeys


def sha1(text: str) -> str:
    '''Returns a sha1 hash object; optionally initialized with a string'''
    sha1 = hashlib.sha1()
    sha1.update(text.encode())
    return sha1.hexdigest()


def sha256(text: str) -> str:
    '''Returns a sha256 hash object; optionally initialized with a string'''
    sha1 = hashlib.sha256()
    sha1.update(text.encode())
    return sha1.hexdigest()


def sha256file(filepath: str) -> str:
    '''Returns a sha256 hash object; optionally initialized with a string'''
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
        return h.hexdigest()


def sha512(text: str) -> str:
    '''Returns a sha512 hash object; optionally initialized with a string'''
    sha1 = hashlib.sha512()
    sha1.update(text.encode())
    return sha1.hexdigest()


def md5(text: str) -> str:
    '''Returns a md5 hash object; optionally initialized with a string'''
    sha1 = hashlib.md5()
    sha1.update(text.encode())
    return sha1.hexdigest()


def md5file(filepath: str) -> str:
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
        return h.hexdigest()
