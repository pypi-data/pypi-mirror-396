#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import hashlib
from urllib.request import urlopen

class MD5():
    @classmethod
    def encrypt(cls, text):
        """
        计算字符的md5摘要
        :param str:
        :return:
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @classmethod
    def encrypt_url(cls, url, max_file_size=100 * 1024 * 1024):
        remote = urlopen(url)
        h = hashlib.md5()

        total_read = 0
        while True:
            data = remote.read(4096)
            total_read += 4096

            if not data or total_read > max_file_size:
                break
            h.update(data)
        return h.hexdigest()

    @classmethod
    def encrypt_file(cls, filename):
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
