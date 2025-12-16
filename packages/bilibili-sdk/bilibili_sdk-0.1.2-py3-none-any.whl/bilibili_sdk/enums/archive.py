#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:

from wpy import Enum, EnumMem


class ArchiveStatus(Enum):
    ALL = EnumMem('is_pubing,pubed,not_pubed', '全部')
    IS_PUBING = EnumMem('is_pubing', '进行中')
    PUBED = EnumMem('pubed', '已发布')
    NOT_PUBED = EnumMem('not_pubed', '未发布')


class ArchiveState(Enum):
    ORANGE_PASS = EnumMem(1, '橙色通过')
    OPEN = EnumMem(0, '开放浏览')
    PENDING_REVIEW = EnumMem(-1, '待审')
    BACKED = EnumMem(-2, '已退回')
    POLICE_LOCKED = EnumMem(-3, '网警锁定')
    LOCKED = EnumMem(-4, '已锁定')
    ADMIN_LOCKED = EnumMem(-5, '管理员锁定')
    #  UPDATED = EnumMem(-6, '修改审核')
    FIX_PENDING_REVIEW = EnumMem(-6, '修复待审')
    TEMPORARY_HOLD = EnumMem(-7, '暂缓审核')
    SUPPLEMENT_PENDING_REVIEW = EnumMem(-8, '补档待审')
    WAITING_TRANSCODE = EnumMem(-9, '等待转码')
    DELAYED_REVIEW = EnumMem(-10, '延迟审核')
    SOURCE_PENDING_FIX = EnumMem(-11, '视频源待修')
    UPLOAD_FAILED = EnumMem(-12, '转储失败')
    COMMENT_PENDING_REVIEW = EnumMem(-13, '允许评论待审')
    TEMPORARY_TRASH = EnumMem(-14, '临时回收站')
    DISTRIBUTING = EnumMem(-15, '分发中')
    TRANSCODE_FAILED = EnumMem(-16, '转码失败')
    CREATED_NOT_SUBMITTED = EnumMem(-20, '创建未提交')
    UNDER_REVIEW = EnumMem(-30, '审核中')
    WAITING = EnumMem(-40, '审核通过，等待发布')
    UPLOADER_VISIBLE = EnumMem(-50, '仅UP主可见')
    USER_DELETED = EnumMem(-100, '用户删除')
