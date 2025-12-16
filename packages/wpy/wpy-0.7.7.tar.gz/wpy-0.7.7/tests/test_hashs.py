#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from wpy import (
    md5, md5file, sha1, sha256, sha512, short
)

CONTENT = 'wxnacy'
FILENAME='tests/test_security.txt'
URL='https://raw.githubusercontent.com/wxnacy/wpy/master/tests/test_security.txt'

def test_hash():
    assert md5(CONTENT) == '1f806eb48b670c40af49a3f764ba086f'

    assert sha1(CONTENT) == 'ae80552bbe355867a1579ab25dfb3a49ac5ffae5'

    assert sha256(CONTENT) == 'e272638378933bcd0921396695cc357a5f8ed7c136d06878d0b9c9ae0302c14a'

    assert sha512(CONTENT) == 'edc44730889e61c7674c6f80c550a865d222ac9214cbb310e61303c5b1fc6bc3ea801a95a3dc2070d2c90aa7a5cae53bbc417b0c10be2e0d33d41d6a68cbf822'

    assert md5file(FILENAME) == '6e7a99c2df5ff33f691eff82623a1152'

def test_short():
    shorts = short(URL)
    assert len(shorts) == 4
    assert shorts[0] == 'VRYQmy'


        #  self.assertEqual(MD5.encrypt_url(URL), '6e7a99c2df5ff33f691eff82623a1152')

        #  shorts = security.short('https://translate.google.cn/#en/zh-CN/random')
        #  print(shorts)

    #  #  def test_aes(self):
        #  #  key = security.AESecurity.generate_key()
        #  #  aes = security.AESecurity(key)
        #  #  security_text = aes.encrypt(CONTENT)
        #  #  plain = aes.decrypt(security_text)
        #  #  self.assertEqual(plain, CONTENT)


#  if __name__ == "__main__":
    #  unittest.main()
