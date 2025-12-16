#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from typing import Self, Optional
from .base import BaseClient
from bilibili_sdk import dto
from bilibili_sdk.config.settings import settings
from .api import ApiClient


class DownloadClient(BaseClient):

    def __init__(self):
        self.api_client = ApiClient.default()

    @classmethod
    def default(cls) -> Self:
        return ApiClient(host=settings.HOST_API)


api_client = ApiClient.default()
