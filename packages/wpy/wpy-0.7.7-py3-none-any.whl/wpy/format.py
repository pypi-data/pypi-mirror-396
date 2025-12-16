#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from typing import (
    Union
)

__all__ = [
    'Format',
    'format_float',
    'format_seconds',
    'format_size',
]

class Format(object):

    @classmethod
    def format_seconds(cls, seconds: int):
        """秒数"""
        #  suffixs = ('B', 'K', 'M', 'G', 'T')
        #  for i in range(5):
            #  if size < 1024 ** ( i + 1 ):
                #  bei_chu = 1024 ** i or 1
                #  res_num = size / bei_chu
                #  if cls._is_int(res_num):
                    #  return '{}{}'.format(int(res_num), suffixs[i])
                #  else:
                    #  return '{:0.2f}{}'.format(res_num, suffixs[i] )
        #  return '{}B'.format(size)

    @classmethod
    def format_size(cls, size: int):
        """格式化文件大小"""
        suffixs = ('B', 'K', 'M', 'G', 'T')
        for i in range(5):
            if size < 1024 ** ( i + 1 ):
                bei_chu = 1024 ** i or 1
                res_num = size / bei_chu
                if cls._is_int(res_num):
                    return '{}{}'.format(int(res_num), suffixs[i])
                else:
                    return '{:0.2f}{}'.format(res_num, suffixs[i] )
        # 超过显示范围的数据按照 B 单位返回
        return '{}B'.format(size)

    @classmethod
    def format_float(cls, float_val: float, decimal_digits: int=2) -> float:
        """格式化 float 数据"""
        if not float_val:
            return float_val
        fmt = '{{:0.{}f}}'.format(decimal_digits)
        return float(fmt.format(float_val))

    @classmethod
    def _is_int(cls, num: Union[int, float]) -> bool:
        if isinstance(num, int):
            return True
        if isinstance(num, float):
            return num == int(num)


format_seconds = Format.format_seconds
format_size = Format.format_size
format_float = Format.format_float


