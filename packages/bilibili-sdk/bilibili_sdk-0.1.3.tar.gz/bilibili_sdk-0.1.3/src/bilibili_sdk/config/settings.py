#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        # 使用 env 字段来指定环境变量名称
        env_prefix="BILIBILI_",
        extra="ignore",
    )
    USER_AGENT: str = Field(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    )
    REFERER: str = Field("https://www.bilibili.com/")
    HOST_API: str = Field("https://api.bilibili.com", title="api 接口 host")
    HOST_MEMBER: str = Field("https://member.bilibili.com", title="member 接口 host")


# 创建 Settings 实例
settings = Settings()


if __name__ == "__main__":
    print(settings.model_dump())
