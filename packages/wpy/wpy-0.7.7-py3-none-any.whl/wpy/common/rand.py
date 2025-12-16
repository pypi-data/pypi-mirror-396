#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import random

LETTERS = [
    'a', 'b',
    'c', 'd', 'e', 'f', 'g', 'h',
    'i', 'j', 'k', 'l', 'm', 'n',
    'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z'
]
NUMS = [
    '1', '2', '3', '4', '5',
    '6', '7', '8', '9', '0'
]
SYMBOLS = [
    '!', '@', '#', '$', '%',
    '^', '&', '*', '(', ')', '-', '=', '+'
]

class Rand():
    @staticmethod
    def rand(strlen):
        str_list = ""
        arr = []
        arr.extend(LETTERS)
        arr.extend(NUMS)
        arr.extend(SYMBOLS)
        for i in range(0, strlen):
            str_list += arr[int(random.uniform(0, len(arr)))]
        return str_list

