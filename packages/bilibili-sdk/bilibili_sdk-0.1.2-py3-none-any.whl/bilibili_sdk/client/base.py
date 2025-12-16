#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:

from aiohttp import ClientResponse
from pydantic import BaseModel
from typing import Dict, Union, Type, Self, Optional, Callable, Any
from wpy import AsyncApiClient
from bilibili_sdk import dto
from bilibili_sdk.config.settings import settings
from bilibili_sdk.common.sign import sign_wbi

ResponseCallback = Callable[[ClientResponse], Any]


class BaseClient(AsyncApiClient):
    cookies: Dict[str, str] = None
    response_callback: ResponseCallback = None

    def __init__(self, host: str):
        super().__init__(host=host)

    class Config():
        HEADERS: dict = {
            'User-Agent': settings.USER_AGENT,
            'Referer': settings.REFERER,
        }

    def set_cookies(self, cookies: dict) -> Self:
        self.cookies = cookies
        return self

    def set_response_callback(self, callback: ResponseCallback) -> Self:
        self.response_callback = callback
        return self

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

        cookies = {}
        if self.cookies:
            cookies.update(self.cookies)
        #  print('cookies:', cookies)

        _headers = {}
        _headers.update(self.Config.HEADERS)
        if headers:
            _headers.update(headers)
        #  print('headers:', _headers)

        res = await super().request(
            method, path,
            params=params,
            data=data,
            headers=_headers,
            cookies=cookies,
            **kwargs,
        )

        # 调用回调接口
        if self.response_callback:
            self.response_callback(res)

        if res_clz:
            res_data = await res.json()
            if res_clz:
                return res_clz(**res_data)

        return res
