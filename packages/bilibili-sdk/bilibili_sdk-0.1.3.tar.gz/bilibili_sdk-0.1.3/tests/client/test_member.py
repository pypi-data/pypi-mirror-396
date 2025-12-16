#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
import pytest

from bilibili_sdk import MemberClient
from bilibili_sdk.dto import GetArchiveListReq
from tests.common import member_client

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_archive_list(member_client: MemberClient):
    req = GetArchiveListReq()
    res = await member_client.get_archive_list(req)
    assert res.is_success

    arc_audits = res.data.arc_audits
    assert len(arc_audits) > 1

    archive = arc_audits[0].archive
    assert archive.mid
    assert archive.aid
    assert archive.bvid

    res = await member_client.get_archive_list(None)
    assert res.is_success

    arc_audits = res.data.arc_audits
    assert len(arc_audits) > 1

    archive = arc_audits[0].archive
    assert archive.mid
    assert archive.aid
    assert archive.bvid


@pytest.mark.asyncio(loop_scope="session")
async def test_get_archive_video_list(member_client: MemberClient):
    req = GetArchiveListReq()
    res = await member_client.get_archive_videos(114019251853794)
    assert res.is_success

    videos = res.data.videos
    assert len(videos) == 4
