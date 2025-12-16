#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:

import os

import pytest
from wpy.path import read_dict

from bilibili_sdk import ApiClient, MemberClient
from bilibili_sdk import api_client as _api_client
from bilibili_sdk import member_client as _member_client

COOKIES_PATH = os.path.expanduser(os.getenv("TEST_BILIBILI_COOKIES_PATH"))


def get_cookies_info():
    data = read_dict(COOKIES_PATH)
    return data


def get_cookies():
    data = read_dict(COOKIES_PATH)
    cookies = data.get("cookie_info").get("cookies")
    cookies_map = {}
    for cookie in cookies:
        cookies_map[cookie.get("name")] = cookie.get("value")
    return cookies_map


def get_api_client() -> ApiClient:
    api_client.set_cookies(get_cookies())
    return api_client


@pytest.fixture(scope="session")
def api_client() -> ApiClient:
    _api_client.set_cookies(get_cookies())
    return _api_client


@pytest.fixture(scope="session")
def member_client() -> MemberClient:
    _member_client.set_cookies(get_cookies())
    return _member_client
