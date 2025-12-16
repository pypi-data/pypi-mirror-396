#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from typing import Self, Optional
from .base import BaseClient
from bilibili_sdk import dto
from bilibili_sdk.config.settings import settings
from bilibili_sdk.common.sign import sign_wbi


class ApiClient(BaseClient):
    #  wbi_img: str
    #  wbi_sub: str

    #  def set_wbi_img(self, img: str) -> Self:
        #  self.wbi_img = img
        #  return self

    #  def set_wbi_sub(self, sub: str) -> Self:
        #  self.wbi_sub = sub
        #  return self
    @classmethod
    def default(cls) -> Self:
        return ApiClient(host=settings.HOST_API)

    async def get_online(self, cid: int, *, aid: int = 0, bvid: str = '') -> dto.GetOnlineRes:
        if not aid and not bvid:
            raise ValueError("aid or bvid 需要有一个有值")
        params = {"cid": cid}
        if bvid:
            params['bvid'] = bvid
        if aid:
            params['aid'] = aid
        return await self.get(
            "/x/player/online/total",
            params=params,
            res_clz=dto.GetOnlineRes,
        )

    async def get_acc_info(self, mid: int, wbi_img: str, wbi_sub: str) -> Optional[dto.GetAccInfoRes]:
        '''用户空间详细信息
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/user/info.md
        '''
        wbi_img = wbi_img.rsplit('/', 1)[-1].split('.')[0]
        wbi_sub = wbi_sub.rsplit('/', 1)[-1].split('.')[0]

        params = {'mid': mid}
        params = sign_wbi(params, wbi_img, wbi_sub)
        return await self.get(
            "/x/space/wbi/acc/info",
            params=params,
            res_clz=dto.GetAccInfoRes,
        )

    async def get_web_inferface_nav(self) -> dto.GetWebInferfaceNavRes:
        '''导航栏用户信息
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/login/login_info.md
        '''
        return await self.get("/x/web-interface/nav", res_clz=dto.GetWebInferfaceNavRes)

    async def get_player_url(self, req: dto.GetPlayerUrlReq) -> dto.GetPlayerUrlRes:
        '''获取视频播放地址
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md
        '''
        return await self.get("/x/player/wbi/playurl", params=req, res_clz=dto.GetPlayerUrlRes)

    async def get_archive_info(self, *, bvid: str = None, aid: int = 0) -> dto.GetArchiveInfoRes:
        '''获取稿件信息
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/info.md
        '''
        params = {"bvid": bvid, "aid": aid}
        return await self.get("/x/web-interface/wbi/view", params=params, res_clz=dto.GetArchiveInfoRes)





api_client = ApiClient.default()
