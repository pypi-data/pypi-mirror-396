#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
import pytest
from wpy import download_async, download
from wpy.hashs import sha256file
from wpy.randoms import random_str

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio(loop_scope="session")
async def test_download_async():
    url = 'https://pypi.tuna.tsinghua.edu.cn/packages/5a/2d/5e92c69f971cb2a373a5203fe2ff0a06751b3eea918c709318e19f7caf62/rich-9.9.0.tar.gz#sha256=0bd8f42c3a03b7ef5e311d5e37f47bea9d268f541981c169072be5869c007957'
    sha256 = '0bd8f42c3a03b7ef5e311d5e37f47bea9d268f541981c169072be5869c007957'

    path = f"/tmp/wpy-{random_str(10)}"
    await download_async(url, path)
    assert sha256 == sha256file(path)

    url = 'https://mirrors.cloud.tencent.com/pypi/packages/39/de/9e95cfd87b026fa59ed0caa16efb6e9f8a1c19a2a59f1a00ffd9cdd0a665/wush-0.2.3.tar.gz#sha256=457b088237e3928de03f0646dee86942c2a2d6e1eca9ac25651a963ce2aa9c6f'
    sha256 = '457b088237e3928de03f0646dee86942c2a2d6e1eca9ac25651a963ce2aa9c6f'
    path = f"/tmp/wpy-{random_str(10)}"
    download(url, path)
    assert sha256 == sha256file(path)
