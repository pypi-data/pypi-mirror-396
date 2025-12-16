#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""
path 模块测试用例
"""

import os
from wpy import path
from wpy.randoms import random_str
from pathlib import Path

test_data_dir = 'tests/data'


def test_walkfile():
    paths = path.walkfile(test_data_dir)
    paths = [o for o in paths]
    assert len(paths) == 4

    paths = path.walkfile(test_data_dir, suffixs=['json'])
    paths = [o for o in paths]
    assert len(paths) == 1


def test_getsize():
    assert path.getsize('tests/data/a.txt') == 7
    assert path.getsize('tests/data/c') == 26

#  def test_write_yml():
    #  """读写"""

    #  data = {"name": "wxnacy"}
    #  _path = f'/tmp/wpy_{random.randint(9000, 10000)}.yml'
    #  path.write_yml(_path, data)

    #  res = path.read_dict(_path)
    #  assert data, res


def test_zip():
    path.zip(test_data_dir, '/tmp')
    assert path.getsize('/tmp/data.zip') == 456

    path.zip('tests/data/', '/tmp')
    assert path.getsize('/tmp/data.zip') == 456

    path.zip(test_data_dir, '/tmp/data2.zip')
    assert path.getsize('/tmp/data2.zip') == 456


def test_rename_download_path():
    # 测试文件
    file = f"/tmp/wpy-{random_str(10)}.mp4"
    newfile = path.rename_download_path(file)
    assert newfile == file
    Path(newfile).touch()

    newfile = path.rename_download_path(file)
    name, ext = os.path.splitext(file)
    assert newfile == f"{name} (1).mp4"
    Path(newfile).touch()

    newfile = path.rename_download_path(file)
    name, ext = os.path.splitext(file)
    assert newfile == f"{name} (2).mp4"
    Path(newfile).touch()

    os.remove(newfile)
    newfile = path.rename_download_path(file)
    name, ext = os.path.splitext(file)
    assert newfile == f"{name} (2).mp4"
    Path(newfile).touch()

    os.remove(file)
    newfile = path.rename_download_path(file)
    name, ext = os.path.splitext(file)
    assert newfile == file
    Path(newfile).touch()

    # 测试文件夹
    file = f"/tmp/wpy-{random_str(10)}"
    newfile = path.rename_download_path(file)
    assert newfile == file
    Path(newfile).touch()

    newfile = path.rename_download_path(file)
    assert newfile == f"{file} (1)"
    Path(newfile).touch()

    newfile = path.rename_download_path(file)
    assert newfile == f"{file} (2)"
    Path(newfile).touch()
