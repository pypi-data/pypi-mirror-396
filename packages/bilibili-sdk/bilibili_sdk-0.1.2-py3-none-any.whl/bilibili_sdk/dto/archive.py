#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from typing import List, Optional, Dict
from pydantic import Field, BaseModel
from bilibili_sdk.enums.archive import ArchiveStatus
from .base import BaseListReq, BaseResponse

class GetArchiveListReq(BaseListReq):
    keyword: str = Field("", title="搜索关键字")
    order: str = Field("senddate", title="")
    status: str = Field(ArchiveStatus.ALL, title="")
    ps: int = Field(10, title="每页条数")
    pn: int = Field(1, title="页码")


class WebOperation(BaseModel):
    id: Optional[int] = Field(default=None)
    icon: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    type: Optional[int] = Field(default=None)
    url: Optional[str] = Field(default=None)
    disabled: Optional[int] = Field(default=None)
    disable_reason: Optional[str] = Field(default=None)

class DisplayField(BaseModel):
    name: Optional[str] = Field(default=None)
    desc: Optional[str] = Field(default=None)
    value: Optional[int] = Field(default=None)
    icon_url: Optional[Dict[str, str]] = Field(default=None)

class Appeal(BaseModel):
    open_apid: Optional[int] = Field(default=None)
    reject: Optional[str] = Field(default=None)
    jump_url: Optional[str] = Field(default=None)

class WebRule(BaseModel):
    more_oper: Optional[List[WebOperation]] = Field(None)

class Archive(BaseModel):
    aid: Optional[int] = Field(default=None)
    bvid: Optional[str] = Field(default=None)
    mid: Optional[int] = Field(default=None)
    tid: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    cover: Optional[str] = Field(default=None)
    reject_reason: Optional[str] = Field(default=None)
    reject_reason_url: Optional[str] = Field(default=None)
    modify_advise: Optional[str] = Field(default=None)
    problem_description: Optional[str] = Field(default=None)
    problem_description_title: Optional[str] = Field(default=None)
    reject_reason_id: Optional[int] = Field(default=None)
    duration: Optional[int] = Field(default=None)
    copyright: Optional[int] = Field(default=None)
    no_reprint: Optional[int] = Field(default=None)
    ugcpay: Optional[int] = Field(default=None)
    online_time: Optional[int] = Field(default=None)
    desc: Optional[str] = Field(default=None)
    forward: Optional[int] = Field(default=None)
    attribute: Optional[int] = Field(default=None)
    state: Optional[int] = Field(default=None, title="状态", description="0 开发浏览 -4 已锁定 -30 审核中、-40 审核通过，等待发布")
    state_desc: Optional[str] = Field(default=None)
    state_panel: Optional[int] = Field(default=None)
    source: Optional[str] = Field(default=None)
    desc_format_id: Optional[int] = Field(default=None)
    attrs: Optional[Dict[str, int]] = Field(default=None)
    dtime: Optional[int] = Field(default=None)
    ptime: Optional[int] = Field(default=None)
    ctime: Optional[int] = Field(default=None)
    interactive: Optional[int] = Field(default=None)
    no_background: Optional[int] = Field(default=None)
    dynamic_video: Optional[int] = Field(default=None)
    limit_state: Optional[bool] = Field(default=None)
    appeal: Optional[str] = Field(default=None)
    appeal_state: Optional[int] = Field(default=None)
    premiere: Optional[int] = Field(default=None)
    is_ugcpay_v2: Optional[int] = Field(default=None)
    political_media: Optional[int] = Field(default=None)
    political_editable: Optional[int] = Field(default=None)
    charging_pay: Optional[int] = Field(default=None)
    charge_2_free: Optional[int] = Field(default=None)
    music_tort: Optional[str] = Field(default=None)
    is_only_self: Optional[int] = Field(default=None)
    is_playlet: Optional[int] = Field(default=None)

class Stat(BaseModel):
    aid: Optional[int] = Field(default=None)
    now_rank: Optional[int] = Field(default=None)
    his_rank: Optional[int] = Field(default=None)
    dislike: Optional[int] = Field(default=None)
    vt: Optional[int] = Field(default=None)
    vv: Optional[int] = Field(default=None)
    view: int = Field(0, title="播放")
    danmaku: int = Field(0, title="弹幕")
    reply: int = Field(0, title="回复")
    favorite: int = Field(0, title="收藏")
    coin: float = Field(0, title="硬币")
    share: int = Field(0, title="分享")
    like: int = Field(0, title="点赞")


class ArcAudit(BaseModel):
    archive: Optional[Archive] = Field(default=None, alias='Archive')
    videos: Optional[List] = Field(default=None, alias='Videos')
    stat: Optional[Stat] = Field(default=None)
    state_panel: Optional[int] = Field(default=None)
    parent_tname: Optional[str] = Field(default=None)
    typename: Optional[str] = Field(default=None)
    open_appeal: Optional[int] = Field(default=None)
    appeal: Optional[Appeal] = Field(default=None)
    fast_pub: Optional[Dict[str, str]] = Field(default=None)
    captions_count: Optional[int] = Field(default=None)
    ai_captions_count: Optional[int] = Field(default=None)
    web_rules: Optional[WebRule] = Field(default=None)
    display_fields: Optional[List[DisplayField]] = Field(default=None)

class ApplyCount(BaseModel):
    neglected: Optional[int] = Field(default=None)
    pending: Optional[int] = Field(default=None)
    processed: Optional[int] = Field(default=None)

class ClassModel(BaseModel):
    pubed: Optional[int] = Field(default=None)
    not_pubed: Optional[int] = Field(default=None)
    is_pubing: Optional[int] = Field(default=None)

class TypeModel(BaseModel):
    tid: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None)
    count: Optional[int] = Field(default=None)

class ArchiveData(BaseModel):
    class_: Optional[ClassModel] = Field(default=None, alias="class")
    apply_count: Optional[ApplyCount] = Field(default=None)
    type_: Optional[List[TypeModel]] = Field(default=None, alias='type')
    archives: Optional[List[Archive]] = Field(default=None)
    arc_audits: Optional[List[ArcAudit]] = Field(default=None)


class GetArchiveListRes(BaseResponse):
    data: Optional[ArchiveData] = Field(default=None)


class Video(BaseModel):
    cid: int = Field(0, title="p1 id")
    title: str = Field("", title="标题")
    filename: str = Field("", title="猜测是md5")
    desc: str = Field("", title="描述")
    index: int = Field(0, title="")
    duraction: int = Field(0, title="时长")


class ArchiveVideoListData(BaseModel):
    archive: Archive = Field(None)
    videos: List[Video] = Field([])

class GetArchiveVideoListRes(BaseResponse):
    data: Optional[ArchiveVideoListData] = Field(default=None)

class Dimension(BaseModel):
    width: Optional[int] = Field(None, title="当前分P 宽度", alias="width")
    height: Optional[int] = Field(None, title="当前分P 高度", alias="height")
    rotate: Optional[int] = Field(None, title="是否将宽高对换", alias="rotate")

class Rights(BaseModel):
    bp: Optional[int] = Field(None, title="是否允许承包", alias="bp")
    elec: Optional[int] = Field(None, title="是否支持充电", alias="elec")
    download: Optional[int] = Field(None, title="是否允许下载", alias="download")
    movie: Optional[int] = Field(None, title="是否电影", alias="movie")
    pay: Optional[int] = Field(None, title="是否PGC付费", alias="pay")
    hd5: Optional[int] = Field(None, title="是否有高码率", alias="hd5")
    no_reprint: Optional[int] = Field(None, title="是否显示禁止转载标志", alias="no_reprint")
    autoplay: Optional[int] = Field(None, title="是否自动播放", alias="autoplay")
    ugc_pay: Optional[int] = Field(None, title="是否UGC付费", alias="ugc_pay")
    is_cooperation: Optional[int] = Field(None, title="是否为联合投稿", alias="is_cooperation")
    ugc_pay_preview: Optional[int] = Field(None, title="作用尚不明确", alias="ugc_pay_preview")
    no_background: Optional[int] = Field(None, title="作用尚不明确", alias="no_background")
    clean_mode: Optional[int] = Field(None, title="作用尚不明确", alias="clean_mode")
    is_stein_gate: Optional[int] = Field(None, title="是否为互动视频", alias="is_stein_gate")
    is_360: Optional[int] = Field(None, title="是否为全景视频", alias="is_360")
    no_share: Optional[int] = Field(None, title="作用尚不明确", alias="no_share")
    arc_pay: Optional[int] = Field(None, title="作用尚不明确", alias="arc_pay")
    free_watch: Optional[int] = Field(None, title="作用尚不明确", alias="free_watch")

class Owner(BaseModel):
    mid: Optional[int] = Field(None, title="UP主mid", alias="mid")
    name: Optional[str] = Field(None, title="UP主昵称", alias="name")
    face: Optional[str] = Field(None, title="UP主头像", alias="face")

class Stat(BaseModel):
    aid: Optional[int] = Field(None, title="稿件avid", alias="aid")
    view: Optional[int] = Field(None, title="播放数", alias="view")
    danmaku: Optional[int] = Field(None, title="弹幕数", alias="danmaku")
    reply: Optional[int] = Field(None, title="评论数", alias="reply")
    favorite: Optional[int] = Field(None, title="收藏数", alias="favorite")
    coin: Optional[int] = Field(None, title="投币数", alias="coin")
    share: Optional[int] = Field(None, title="分享数", alias="share")
    now_rank: Optional[int] = Field(None, title="当前排名", alias="now_rank")
    his_rank: Optional[int] = Field(None, title="历史最高排行", alias="his_rank")
    like: Optional[int] = Field(None, title="获赞数", alias="like")
    dislike: Optional[int] = Field(None, title="点踩数", alias="dislike")
    evaluation: Optional[str] = Field(None, title="视频评分", alias="evaluation")
    vt: Optional[int] = Field(None, title="作用尚不明确", alias="vt")

class Page(BaseModel):
    cid: Optional[int] = Field(None, title="分P cid", alias="cid")
    page: Optional[int] = Field(None, title="分P序号", alias="page")
    from_: Optional[str] = Field(None, title="视频来源", alias="from")
    part: Optional[str] = Field(None, title="分P标题", alias="part")
    duration: Optional[int] = Field(None, title="分P持续时间", alias="duration")
    vid: Optional[str] = Field(None, title="站外视频vid", alias="vid")
    weblink: Optional[str] = Field(None, title="站外视频跳转url", alias="weblink")
    dimension: Optional[Dimension] = Field(None, title="当前分P分辨率", alias="dimension")

class SubtitleAuthor(BaseModel):
    mid: Optional[int] = Field(None, title="字幕上传者mid", alias="mid")
    name: Optional[str] = Field(None, title="字幕上传者昵称", alias="name")
    sex: Optional[str] = Field(None, title="字幕上传者性别", alias="sex")
    face: Optional[str] = Field(None, title="字幕上传者头像url", alias="face")
    sign: Optional[str] = Field(None, title="字幕上传者签名", alias="sign")
    rank: Optional[int] = Field(None, title="作用尚不明确", alias="rank")
    birthday: Optional[int] = Field(None, title="作用尚不明确", alias="birthday")
    is_fake_account: Optional[int] = Field(None, title="作用尚不明确", alias="is_fake_account")
    is_deleted: Optional[int] = Field(None, title="作用尚不明确", alias="is_deleted")

class SubtitleItem(BaseModel):
    id: Optional[int] = Field(None, title="字幕id", alias="id")
    lan: Optional[str] = Field(None, title="字幕语言", alias="lan")
    lan_doc: Optional[str] = Field(None, title="字幕语言名称", alias="lan_doc")
    is_lock: Optional[bool] = Field(None, title="是否锁定", alias="is_lock")
    author_mid: Optional[int] = Field(None, title="字幕上传者mid", alias="author_mid")
    subtitle_url: Optional[str] = Field(None, title="json格式字幕文件url", alias="subtitle_url")
    author: Optional[SubtitleAuthor] = Field(None, title="字幕上传者信息", alias="author")

class Subtitle(BaseModel):
    allow_submit: Optional[bool] = Field(None, title="是否允许提交字幕", alias="allow_submit")
    list: Optional[List[SubtitleItem]] = Field(None, title="字幕列表", alias="list")

class StaffVIP(BaseModel):
    type: Optional[int] = Field(None, title="成员会员类型", alias="type")
    status: Optional[int] = Field(None, title="会员状态", alias="status")
    due_date: Optional[int] = Field(None, title="到期时间", alias="due_date")
    vip_pay_type: Optional[int] = Field(None, title="作用尚不明确", alias="vip_pay_type")
    theme_type: Optional[int] = Field(None, title="作用尚不明确", alias="theme_type")
    label: Optional[Dict] = Field(None, title="作用尚不明确", alias="label")

class StaffOfficial(BaseModel):
    role: Optional[int] = Field(None, title="成员认证级别", alias="role")
    title: Optional[str] = Field(None, title="成员认证名", alias="title")
    desc: Optional[str] = Field(None, title="成员认证备注", alias="desc")
    type: Optional[int] = Field(None, title="成员认证类型", alias="type")

class StaffItem(BaseModel):
    mid: Optional[int] = Field(None, title="成员mid", alias="mid")
    title: Optional[str] = Field(None, title="成员名称", alias="title")
    name: Optional[str] = Field(None, title="成员昵称", alias="name")
    face: Optional[str] = Field(None, title="成员头像url", alias="face")
    vip: Optional[StaffVIP] = Field(None, title="成员大会员状态", alias="vip")
    official: Optional[StaffOfficial] = Field(None, title="成员认证信息", alias="official")
    follower: Optional[int] = Field(None, title="成员粉丝数", alias="follower")
    label_style: Optional[int] = Field(None, title="作用尚不明确", alias="label_style")

class HonorItem(BaseModel):
    aid: Optional[int] = Field(None, title="当前稿件aid", alias="aid")
    type: Optional[int] = Field(None, title="荣誉类型", alias="type")
    desc: Optional[str] = Field(None, title="描述", alias="desc")
    weekly_recommend_num: Optional[int] = Field(None, title="作用尚不明确", alias="weekly_recommend_num")

class ArgueInfo(BaseModel):
    argue_link: Optional[str] = Field(None, title="作用尚不明确", alias="argue_link")
    argue_msg: Optional[str] = Field(None, title="警告/争议提示信息", alias="argue_msg")
    argue_type: Optional[int] = Field(None, title="作用尚不明确", alias="argue_type")

class DescV2(BaseModel):
    raw_text: Optional[str] = Field(None, title="简介内容", alias="raw_text")
    type: Optional[int] = Field(None, title="类型", alias="type")
    biz_id: Optional[int] = Field(None, title="被@用户的mid", alias="biz_id")

class ArchiveInfo(BaseModel):
    bvid: Optional[str] = Field(None, title="稿件bvid", alias="bvid")
    aid: Optional[int] = Field(None, title="稿件avid", alias="aid")
    videos: Optional[int] = Field(None, title="稿件分P总数", alias="videos")
    tid: Optional[int] = Field(None, title="分区tid", alias="tid")
    tname: Optional[str] = Field(None, title="子分区名称", alias="tname")
    copyright: Optional[int] = Field(None, title="视频类型", alias="copyright")
    pic: Optional[str] = Field(None, title="稿件封面图片url", alias="pic")
    title: Optional[str] = Field(None, title="稿件标题", alias="title")
    pubdate: Optional[int] = Field(None, title="稿件发布时间", alias="pubdate")
    ctime: Optional[int] = Field(None, title="用户投稿时间", alias="ctime")
    desc: Optional[str] = Field(None, title="视频简介", alias="desc")
    desc_v2: Optional[List[DescV2]] = Field(None, title="新版视频简介", alias="desc_v2")
    state: Optional[int] = Field(None, title="视频状态", alias="state")
    attribute: Optional[int] = Field(None, title="稿件属性位配置", alias="attribute")
    duration: Optional[int] = Field(None, title="稿件总时长", alias="duration")
    forward: Optional[int] = Field(None, title="撞车视频跳转avid", alias="forward")
    mission_id: Optional[int] = Field(None, title="稿件参与的活动id", alias="mission_id")
    redirect_url: Optional[str] = Field(None, title="重定向url", alias="redirect_url")
    rights: Optional[Rights] = Field(None, title="视频属性标志", alias="rights")
    owner: Optional[Owner] = Field(None, title="视频UP主信息", alias="owner")
    stat: Optional[Stat] = Field(None, title="视频状态数", alias="stat")
    dynamic: Optional[str] = Field(None, title="视频同步发布的动态的文字内容", alias="dynamic")
    cid: Optional[int] = Field(None, title="视频1P cid", alias="cid")
    dimension: Optional[Dimension] = Field(None, title="视频1P分辨率", alias="dimension")
    teenage_mode: Optional[int] = Field(None, title="用于青少年模式", alias="teenage_mode")
    is_chargeable_season: Optional[bool] = Field(None, title="作用尚不明确", alias="is_chargeable_season")
    is_story: Optional[bool] = Field(None, title="是否可以在Story Mode展示", alias="is_story")
    is_upower_exclusive: Optional[bool] = Field(None, title="是否为充电专属", alias="is_upower_exclusive")
    is_upower_pay: Optional[bool] = Field(None, title="作用尚不明确", alias="is_upower_pay")
    is_upower_show: Optional[bool] = Field(None, title="作用尚不明确", alias="is_upower_show")
    no_cache: Optional[bool] = Field(None, title="是否不允许缓存", alias="no_cache")
    pages: Optional[List[Page]] = Field(None, title="视频分P列表", alias="pages")
    subtitle: Optional[Subtitle] = Field(None, title="视频CC字幕信息", alias="subtitle")
    staff: Optional[List[StaffItem]] = Field(None, title="合作成员列表", alias="staff")
    is_season_display: Optional[bool] = Field(None, title="作用尚不明确", alias="is_season_display")
    user_garb: Optional[Dict] = Field(None, title="用户装扮信息", alias="user_garb")
    honor_reply: Optional[Dict] = Field(None, title="作用尚不明确", alias="honor_reply")
    like_icon: Optional[str] = Field(None, title="作用尚不明确", alias="like_icon")
    need_jump_bv: Optional[bool] = Field(None, title="需要跳转到BV号", alias="need_jump_bv")
    disable_show_up_info: Optional[bool] = Field(None, title="禁止展示UP主信息", alias="disable_show_up_info")
    is_story_play: Optional[bool] = Field(None, title="是否为Story Mode视频", alias="is_story_play")
    is_view_self: Optional[bool] = Field(None, title="是否为自己投稿的视频", alias="is_view_self")
    argue_info: Optional[ArgueInfo] = Field(None, title="争议/警告信息", alias="argue_info")

class GetArchiveInfoRes(BaseResponse):
    data: Optional[ArchiveInfo] = Field(default=None)
