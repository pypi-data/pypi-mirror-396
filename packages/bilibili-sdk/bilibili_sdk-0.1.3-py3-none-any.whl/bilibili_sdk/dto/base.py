#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:

from typing import Any
from pydantic import BaseModel, Field, SkipValidation


class BaseResponse(BaseModel):
    code: int = Field(0, title="状态")
    ttl: int = Field(1, title="状态")
    message: str = Field("", title="信息")
    data: SkipValidation[Any] = Field(None, title="数据")

    @property
    def is_success(self):
        """The is_success property."""
        return self.code == 0

    def pprint(self):
        print(self.model_dump_json(indent=4))


class BaseListReq(BaseModel):
    pn: int = Field(1)
    ps: int = Field(10)
