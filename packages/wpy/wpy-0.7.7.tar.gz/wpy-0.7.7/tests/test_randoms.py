#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
随机方法
"""

import pytest

from wpy.randoms import RandomUtils
from collections import defaultdict

def test_random_int():
    """随机 int 值"""
    res = RandomUtils.random_int(3)
    assert len(res) == 3

    res = RandomUtils.random_int(100, 3, 8)
    for i in res:
        assert 3 <= int(i) <= 8

    with pytest.raises(ValueError) as excinfo:
        RandomUtils.random_int(1, -1)
        assert str(excinfo) == 'random_int min_int must >= 0'

    with pytest.raises(ValueError) as excinfo:
        RandomUtils.random_int(1, max_int = 11)
        assert str(excinfo) == 'random_int max_int must <= 9'

    with pytest.raises(ValueError) as excinfo:
        RandomUtils.random_int(1, min_int = 5, max_int = 1)
        assert str(excinfo) == 'random_int max_int must > min_int'

def test_random_str():
    """随机字符串"""
    res = RandomUtils.random_int(30)
    assert len(res) == 30

    all_letters = [chr(o) for o in range(65, 91)]
    all_letters.extend([chr(o) for o in range(97, 123)])
    all_letters.extend([str(o) for o in range(0, 10)])
    all_letters.extend(['!', '@', '#', '$', '%', '^', '&', '*', '(', ')'])

    count_map = defaultdict(int)
    res = RandomUtils.random_str(1000)
    for lt in res:
        count_map[lt] += 1

    for lt in all_letters:
        count = count_map.get(lt, 0)
        assert count > 0

    with pytest.raises(ValueError) as excinfo:
        RandomUtils.random_str(3, '')
        assert str(excinfo) == 'letters len must > 0'
