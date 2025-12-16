#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:

from typing import Dict, Optional, Callable, Union
import requests
from requests import Response
from aiohttp import ClientSession, ClientResponse

TotalSize = int
ChunkSize = int
SuccessFunc = Callable[[Union[Response, ClientResponse], TotalSize], None]
ProgressFunc = Callable[[Union[Response, ClientResponse], ChunkSize], None],


def download(
    url: str,
    save_path: str,
    *,
    headers: Optional[Dict] = None,
    success_callback: SuccessFunc = None,
    progress_callback: ProgressFunc = None,
):
    """带进度条的下载文件"""
    res = requests.get(url, headers=headers, stream=True)
    if success_callback:
        total_size = int(res.headers.get("Content-Length", 0))
        success_callback(res, total_size)
    with open(save_path, "wb") as dest_file:
        for chunk in res.iter_content(chunk_size=8*1024):
            if chunk:
                dest_file.write(chunk)
                if progress_callback:
                    progress_callback(res, len(chunk))

    return res


async def download_async(
    url: str,
    save_path: str,
    *,
    headers: Optional[Dict] = None,
    success_callback: SuccessFunc = None,
    progress_callback: ProgressFunc = None,
):
    """
    异步下载文件，并更新进度条
    """
    session = ClientSession(
        raise_for_status=True
    )
    try:
        async with session.get(
            url,
            headers=headers,
        ) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            if success_callback:
                await success_callback(response, total_size)
            with open(save_path, "wb") as file:
                while True:
                    chunk = await response.content.read(8*1024)
                    if not chunk:
                        break
                    file.write(chunk)
                    if progress_callback:
                        await progress_callback(response, len(chunk))
    except Exception as e:
        raise e
    finally:
        await session.close()
