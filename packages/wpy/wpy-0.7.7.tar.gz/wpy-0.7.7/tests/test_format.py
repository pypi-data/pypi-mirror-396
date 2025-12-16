#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
格式化模块
"""


from wpy import format_size, format_float
from wpy.format import Format

def test_format_size():
    """格式化 size"""

    assert '102B' == format_size(102)
    assert '1K' == format_size(1024)
    assert '1.98K' == format_size(2024)
    assert '1.86M' == format_size(1024 **2 + 900000)
    assert '1.84G' == format_size(1024 **3 + 900000000)
    assert '1.39T' == format_size(1024 **4 + 1024 ** 3 * 400)

    size = 1024 **4 + 1024 ** 3 * 400 * 1024 * 1024
    assert '{}B'.format(size) == format_size(size)

def test_is_int():
    assert Format._is_int(1)
    assert Format._is_int(1.0)
    assert not Format._is_int(1.1)

    #  import time
    #  b = time.time()
    #  for i in range(1000000):
        #  Format._is_int(1.234567)
    #  print(time.time() - b)

def test_format_float():

    assert format_float(0.0) == 0.0

    assert format_float(1.2345) == 1.23

    assert format_float(1.2375) == 1.24

    assert format_float(1.2346, decimal_digits = 3) == 1.235
