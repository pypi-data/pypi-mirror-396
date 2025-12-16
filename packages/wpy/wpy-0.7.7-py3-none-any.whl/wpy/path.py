#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""
路径相关模块
"""
import zipfile
import os
import json
#  import yaml

__all__ = [
    'zip', 'unzip', 'read_dict', 'write_dict', 'walkfile',
    'getsize'
]


def read_dict(filepath):
    """
    读取字典数据
    :param str filepath: 文件地址
    """
    with open(filepath, 'r') as f:
        #  if filepath.endswith('.yml'):
        #  return yaml.safe_load(f)
        lines = f.readlines()
    return json.loads(''.join(lines))

#  def write_yml(filepath, data):
    #  """保存成 yml 格式文件"""
    #  filepath = os.path.expanduser(filepath)
    #  with open(filepath, 'w') as f:
    #  yaml.dump(data, f)


def write_dict(filepath, data):
    """保存成 dict 格式文件"""
    filepath = os.path.expanduser(filepath)
    with open(filepath, 'w') as f:
        f.write(json.dumps(data, indent=4))


def walkfile(dirname, suffixs=None):
    """
    迭代文件
    """
    if not suffixs:
        suffixs = []

    for _dir, _, names in os.walk(dirname):
        for name in names:
            path = os.path.join(_dir, name)
            suf = path.rsplit('.', 1)[1]
            if suffixs and isinstance(suffixs, list):
                if suf not in suffixs:
                    continue
            yield path


def getsize(filepath):
    filepath = os.path.expanduser(filepath)
    if os.path.isfile(filepath):
        return os.path.getsize(filepath)
    if os.path.isdir(filepath):
        total = 0
        for path in walkfile(filepath):
            total += os.path.getsize(path)
        return total


def unzip(zip_path, to_dir=None):
    """解压文件"""
    if not to_dir:
        to_dir = os.path.dirname(zip_path)

    z = zipfile.ZipFile(zip_path)
    z.extractall(to_dir)
    z.close()
    return to_dir


def zip(from_path, to_path=None):
    """
    压缩文件,
    :param path:
    :param is_empty: 压缩附件时使用，附件可能为空
    :return:
    """
    pwd = os.getcwd()
    if from_path.endswith('/'):
        from_path = from_path[:-1]
    if not to_path:
        to_path = from_path + '.zip'
    if os.path.isdir(to_path):
        to_path = os.path.join(to_path, os.path.basename(from_path) + '.zip')
    isdir = os.path.isdir(from_path)
    if isdir:
        return _zip_dir(from_path, to_path)

    dirname, filename = os.path.split(from_path)
    os.chdir(dirname)

    z = zipfile.ZipFile(to_path, 'w', allowZip64=True)
    z.write(filename)
    z.close()
    os.chdir(pwd)
    return to_path


def _zip_dir(from_path, to_path):
    pwd = os.getcwd()
    dirname, basename = os.path.split(from_path)
    os.chdir(dirname)
    z = zipfile.ZipFile(to_path, 'w', allowZip64=True)
    for dirpath, dirnames, filenames in os.walk(basename):
        for filename in filenames:
            z.write(os.path.join(dirpath, filename))
    z.close()
    os.chdir(pwd)
    return to_path


def rename_download_path(path: str) -> str:
    '''对下载地址重新命名
    ```python
    path = rename_download_path("test.mp4")
    assert path == "test.mp4"

    path = rename_download_path("test.mp4")
    assert path == "test (1).mp4"

    path = rename_download_path("test.mp4")
    assert path == "test (2).mp4"

    path = rename_download_path("test")
    assert path == "test"

    path = rename_download_path("test")
    assert path == "test (1)"
    ```
    '''

    temp = path
    name, ext = os.path.splitext(temp)
    for i in range(100000000):
        if i > 0:
            temp = f"{name} ({i})" + (ext if ext else "")

        if not os.path.exists(temp):
            return temp
