#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
import pytest
from rich import print

from bilibili_sdk import ApiClient, dto
from tests.common import api_client, get_cookies_info

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio(loop_scope="module")
async def test_get_web_inferface_nav(api_client: ApiClient):
    info = get_cookies_info()
    res = await api_client.get_web_inferface_nav()
    assert res.is_success

    data = res.data
    assert data.mid == info.get("token_info").get("mid")

    img = data.wbi_img.img_url
    img = img.rsplit("/", 1)[-1].split(".")[0]
    sub = data.wbi_img.sub_url
    sub = sub.rsplit("/", 1)[-1].split(".")[0]
    res = await api_client.get_acc_info(data.mid, img, sub)
    assert res.is_success


@pytest.mark.asyncio(loop_scope="module")
async def test_get_online(api_client: ApiClient):
    res = await api_client.get_online(1313229659, aid=365244281)
    assert res.is_success

    data = res.data
    assert data.total == "1"
    assert data.count == "1"


@pytest.mark.asyncio(loop_scope="module")
async def test_get_player_url(api_client: ApiClient):
    req = dto.GetPlayerUrlReq(
        cid=28441382320,
        bvid="BV1SPwdevE1R",
        fnval=16,
    )
    res: dto.GetPlayerUrlRes = await api_client.get_player_url(req)
    assert res.is_success

    data = res.data
    assert len(data.support_formats) == len(data.accept_description)
    print(data)


@pytest.mark.asyncio(loop_scope="module")
async def test_get_archive_info(api_client: ApiClient):
    bvid = "BV1SPwdevE1R"
    res: dto.GetArchiveInfoRes = await api_client.get_archive_info(bvid=bvid)
    assert res.is_success

    data = res.data
    assert data.bvid == bvid
    print(data)
