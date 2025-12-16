#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from typing import Self, Optional
from .base import BaseClient
from bilibili_sdk import dto
from bilibili_sdk.config.settings import settings
from bilibili_sdk.common.sign import sign_wbi


class MemberClient(BaseClient):

    @classmethod
    def default(cls) -> Self:
        return MemberClient(host=settings.HOST_MEMBER)

    async def get_archive_list(self, req: Optional[dto.GetArchiveListReq]) -> dto.GetArchiveListRes:
        """获取稿件列表
        从创作中心-稿件管理中获取
        需要用户cookies信息
        https://member.bilibili.com/platform/upload-manager/article
        """
        if not req:
            req = dto.GetArchiveListReq()
        return await self.get(
            "/x/web/archives",
            params=req,
            res_clz=dto.GetArchiveListRes
        )

    async def get_archive_videos(self, aid: int) -> dto.GetArchiveVideoListRes:
        '''获取稿件视频列表'''
        return await self.get(
            "/x/web/archive/videos",
            params={"aid": aid},
            res_clz=dto.GetArchiveVideoListRes
        )



member_client = MemberClient(host=settings.HOST_MEMBER)
