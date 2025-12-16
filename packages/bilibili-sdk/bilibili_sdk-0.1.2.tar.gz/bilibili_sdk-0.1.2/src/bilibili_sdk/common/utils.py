#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from urllib.parse import urlparse

def get_bvid(text: str):
    if text.startswith('BV'):
        return text
    if text.startswith('http'):
        parse = urlparse(text)
        paths = parse.path.split('/')
        for item in paths:
            if item.startswith('BV'):
                return item
    return None

