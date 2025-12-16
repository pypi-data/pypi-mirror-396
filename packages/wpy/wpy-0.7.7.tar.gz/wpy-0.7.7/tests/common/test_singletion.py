#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:

from wpy import Singleton


class Test(Singleton):
    pass


def test_singletion():
    t1 = Test()
    t2 = Test()

    assert t1 == t2
