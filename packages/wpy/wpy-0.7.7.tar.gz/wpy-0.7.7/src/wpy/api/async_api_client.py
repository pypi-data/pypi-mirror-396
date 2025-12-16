#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:

import asyncio
from typing import Type, Union, Dict
from pydantic import BaseModel
from aiohttp import ClientError, ClientSession


class AsyncApiClient:

    def __init__(self, host: str):
        self.host = host
        self.max_retries = 3
        self.retry_interval = 1

    async def post(
        self,
        path: str,
        *,
        data: Union[dict, BaseModel] = None,
        headers: Union[dict, BaseModel] = None,
        res_clz: Type[BaseModel] = None,
        **kwargs
    ) -> Union[BaseModel, Dict]:
        return await self.request(
            'POST',
            path,
            data=data,
            headers=headers,
            res_clz=res_clz,
        )

    async def get(
        self,
        path: str,
        *,
        params: Union[dict, BaseModel] = None,
        headers: Union[dict, BaseModel] = None,
        res_clz: Type[BaseModel] = None,
        **kwargs
    ) -> Union[BaseModel, Dict]:
        return await self.request(
            'GET',
            path,
            params=params,
            headers=headers,
            res_clz=res_clz
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Union[dict, BaseModel] = None,
        data: Union[dict, BaseModel] = None,
        headers: Union[dict, BaseModel] = None,
        res_clz: Type[BaseModel] = None,
        **kwargs
    ) -> Union[BaseModel, Dict]:
        url = path
        if isinstance(data, BaseModel):
            data = data.model_dump(by_alias=True, exclude_none=True)
        if isinstance(headers, BaseModel):
            headers = headers.model_dump(by_alias=True, exclude_none=True)
        if isinstance(params, BaseModel):
            params = params.model_dump(by_alias=True, exclude_none=True)
        log_prefix = f"digibuy {path}"
        #  logger.info(f"{log_prefix} request params: {json.dumps(params, ensure_ascii=False)}")
        #  logger.info(f"{log_prefix} request data: {json.dumps(data, ensure_ascii=False)}")
        #  logger.info(f"{log_prefix} headers: {headers}")

        for attempt in range(self.max_retries):
            session = ClientSession(
                base_url=self.host,
                raise_for_status=True
            )
            try:
                async with session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                    **kwargs
                ) as res:
                    res_data = await res.json()
                    import json
                    #  print(f"{log_prefix} response {json.dumps(res_data, ensure_ascii=False, indent=4)}")
                    if res_clz:
                        return res_clz(**res_data)
                    return res

            except (ClientError, asyncio.TimeoutError) as e:
                if attempt < self.max_retries - 1:
                    #  logger.info(f"{log_prefix} 请求失败，正在尝试第{attempt + 2}次链接...")
                    await asyncio.sleep(self.retry_interval)
                else:
                    #  logger.error(f"{log_prefix} {traceback.format_exc()}")
                    #  logger.error(f"{log_prefix} {traceback.format_stack()}")
                    raise e
            finally:
                await session.close()

        return None
