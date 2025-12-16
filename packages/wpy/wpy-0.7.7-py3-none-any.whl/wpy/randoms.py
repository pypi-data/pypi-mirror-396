#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
随机方法
"""

import random

__all__ = [
    "RandomUtils",
    "random_int",
    "random_str",
]

class RandomUtils(object):

    @classmethod
    def random_int(cls, length, min_int=None, max_int=None):
        """随机 int 值"""
        if min_int is None:
            min_int = 0
        if max_int is None:
            max_int = 9

        if min_int < 0:
            raise ValueError('random_int min_int must >= 0')

        if max_int > 9:
            raise ValueError('random_int max_int must <= 9')

        if min_int >= max_int:
            raise ValueError('random_int max_int must > min_int')
        res = []
        for _ in range(length):
            n = random.randint(min_int, max_int)
            res.append(str(n))
        return ''.join(res)

    @classmethod
    def random_str(cls, length, letters=None):
        """随机 str 值"""
        if letters is None:
            letters = 'a-z,A-Z,0-9,!@#$%^&*()'
        res = []
        random_letters = []
        for letter in letters.split(","):
            if '-' in letter:
                min_lt, max_lt = letter.split('-')
                random_letters.extend(chr(o) for o in range(ord(min_lt),
                    ord(max_lt) + 1))
            else:
                random_letters.extend([o for o in letter])

        if not random_letters:
            raise ValueError('letters len must > 0')

        for _ in range(length):
            n = random.randint(0, len(random_letters) - 1)
            res.append(random_letters[n])
        return ''.join(res)

random_int = RandomUtils.random_int
random_str = RandomUtils.random_str
