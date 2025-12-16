#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
import pytest
from bilibili_sdk import utils

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_bvid():
    text = 'BV1SPwdevE1R'
    assert utils.get_bvid(text) == text

    text = 'https://www.bilibili.com/video/BV1SPwdevE1R/?vd_source=4caaf34848771d6fb4996e6e3776a490'
    assert utils.get_bvid(text) == 'BV1SPwdevE1R'
