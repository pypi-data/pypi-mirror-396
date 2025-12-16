#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:  常用的装饰器

import timeit
import pkgutil
import subprocess
from typing import (
    Callable
)

__all__ = ['clock', 'run_shell', 'find_modules']

CLOCK_FMT = '[{T:0.8f}s] {F}({A}, {K}) -> {R}'

def clock(times: int=1, fmt: str=CLOCK_FMT, logger_func: Callable=print):
    '''函数计时器'''
    def clock_wraper(func):
        def _wraper(*args, **kwargs):
            t0 = timeit.default_timer()
            result = None
            for i in range(times):
                result = func(*args, **kwargs)
            T = timeit.default_timer() - t0
            F = func.__name__
            A = args
            K = kwargs
            R = repr(result)
            logger_func(fmt.format(**locals()))
            return result
        return _wraper
    return clock_wraper

def find_modules(paths):
    '''查找路径下的所有 module'''
    if isinstance(paths, str):
        paths = [paths]
    for finder, name, ispkg in pkgutil.iter_modules(paths):
        #  print(finder, name, ispkg)
        if ispkg:
            subpath = '{}/{}'.format(finder.path, name)
            yield from find_modules(subpath)
        else:
            module_path = '{}/{}'.format(finder.path, name)
            yield module_path.replace('/', '.')

def run_shell(command: str) -> tuple:
    """运行 shell 语句"""
    res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
        stderr = subprocess.PIPE)
    return res.communicate()

if __name__ == "__main__":
    #  @clock()
    #  def test(*args, **kw):
        #  r = 0
        #  for i in range(10000):
            #  r += i

    #  test(1, 'a')

    for m in find_modules('tests'):
        print(m)


