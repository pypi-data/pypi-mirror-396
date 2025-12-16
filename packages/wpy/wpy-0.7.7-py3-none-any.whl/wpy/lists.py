#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""
list 工具模块
"""

from functools import cmp_to_key
from collections import defaultdict

__all__ = [
    "ListUtils",
    "sorted_plus",
    "search",
]

class ListUtils(object):

    @classmethod
    def sorted_plus(cls, arr, sorter=None, reverse=False):
        """
        排序
        :param list arr: 数组
        :param list sorter: 排序方式
            [('age', 1), ('id', -1)]    age 按照正序，相同时 id 倒序
        :param bool reverse: 是否倒序
        """
        def _sort(a, b):
            for name, sort_by in sorter:
                a_val = a.get(name)
                b_val = b.get(name)
                if a_val is None:
                    return -sort_by
                if b_val is None:
                    return sort_by
                if a_val < b_val:
                    return -sort_by
                elif a_val > b_val:
                    return sort_by

            return 0

        if sorter:
            arr.sort(key=cmp_to_key(_sort))
        else:
            arr.sort(reverse = reverse)

        return arr

sorted_plus = ListUtils.sorted_plus

def search(datas, word):
    """
    检索文本列表中包含 word 的元素，并按照匹配度排序返回
    :param list datas: 文本列表
    :param str word: 搜索的单词
    :results list 搜索结果，按照匹配位置排序

    >>> search(["123wxn", "wxn", "test"], "wxn")
    >>> ["wxn", "123wxn"]
    """
    patten = defaultdict(int)
    for o in datas:
        patten[o] = -1
        p = o.lower()
        if word not in p:
            continue
        patten[o] = p.index(word)
    res = list(filter(lambda x: patten[x] > -1, datas))
    res.sort(key = lambda x: patten[x])
    return res

