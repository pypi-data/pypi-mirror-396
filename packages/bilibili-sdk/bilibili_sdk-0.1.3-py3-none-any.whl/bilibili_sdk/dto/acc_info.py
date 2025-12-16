#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseResponse


class Official(BaseModel):
    role: Optional[int] = Field(default=None, description="认证类型")
    title: Optional[str] = Field(default="", description="认证信息，无为空")
    desc: Optional[str] = Field(default="", description="认证备注，无为空")
    type: Optional[int] = Field(default=None, description="是否认证：-1：无, 0：个人认证, 1：机构认证")


class VipLabel(BaseModel):
    path: Optional[str] = Field(default="", description="空，作用尚不明确")
    text: Optional[str] = Field(default="", description="会员类型文案")
    label_theme: Optional[str] = Field(default="", description="会员标签")
    text_color: Optional[str] = Field(default="", description="会员标签颜色")
    bg_style: Optional[int] = Field(default=1, description="背景样式")
    bg_color: Optional[str] = Field(default="", description="会员标签背景颜色")
    border_color: Optional[str] = Field(default="", description="会员标签边框颜色，未使用")
    use_img_label: Optional[bool] = Field(default=True, description="是否使用图片标签")
    img_label_uri_hans: Optional[str] = Field(default="", description="空串")
    img_label_uri_hant: Optional[str] = Field(default="", description="空串")
    img_label_uri_hans_static: Optional[str] = Field(default="", description="大会员牌子图片，简体版")
    img_label_uri_hant_static: Optional[str] = Field(default="", description="大会员牌子图片，繁体版")


class Vip(BaseModel):
    type: Optional[int] = Field(default=0, description="会员类型：0：无, 1：月大会员, 2：年度及以上大会员")
    status: Optional[int] = Field(default=0, description="会员状态：0：无, 1：有")
    due_date: Optional[int] = Field(default=0, description="会员过期时间，毫秒时间戳")
    vip_pay_type: Optional[int] = Field(default=0, description="支付类型：0：未支付, 1：已支付")
    theme_type: Optional[int] = Field(default=0, description="作用尚不明确")
    label: Optional[VipLabel] = Field(default=None, description="会员标签")
    avatar_subscript: Optional[int] = Field(default=0, description="是否显示会员图标")
    nickname_color: Optional[str] = Field(default="#FB7299", description="会员昵称颜色")
    role: Optional[int] = Field(default=1, description="大角色类型：1：月度大会员, 3：年度大会员, 7：十年大会员, 15：百年大会员")
    avatar_subscript_url: Optional[str] = Field(default="", description="大会员角标地址")
    tv_vip_status: Optional[int] = Field(default=0, description="电视大会员状态：0：未开通")
    tv_vip_pay_type: Optional[int] = Field(default=None, description="电视大会员支付类型")


class Pendant(BaseModel):
    pid: Optional[int] = Field(default=None, description="头像框id")
    name: Optional[str] = Field(default="", description="头像框名称")
    image: Optional[str] = Field(default="", description="头像框图片url")
    expire: Optional[int] = Field(default=0, description="过期时间，此接口返回恒为0")
    image_enhance: Optional[str] = Field(default="", description="头像框图片url")
    image_enhance_frame: Optional[str] = Field(default="", description="头像框图片逐帧序列url")


class Nameplate(BaseModel):
    nid: Optional[int] = Field(default=None, description="勋章id")
    name: Optional[str] = Field(default="", description="勋章名称")
    image: Optional[str] = Field(default="", description="勋章图标")
    image_small: Optional[str] = Field(default="", description="勋章图标（小）")
    level: Optional[str] = Field(default="", description="勋章等级")
    condition: Optional[str] = Field(default="", description="获取条件")


class Medal(BaseModel):
    uid: Optional[int] = Field(default=None, description="此用户mid")
    target_id: Optional[int] = Field(default=None, description="粉丝勋章所属UP的mid")
    medal_id: Optional[int] = Field(default=None, description="粉丝勋章id")
    level: Optional[int] = Field(default=None, description="粉丝勋章等级")
    medal_name: Optional[str] = Field(default="", description="粉丝勋章名称")
    medal_color: Optional[int] = Field(default=None, description="颜色")
    intimacy: Optional[int] = Field(default=None, description="当前亲密度")
    next_intimacy: Optional[int] = Field(default=None, description="下一等级所需亲密度")
    day_limit: Optional[int] = Field(default=None, description="每日亲密度获取上限")
    today_feed: Optional[int] = Field(default=None, description="今日已获得亲密度")
    medal_color_start: Optional[int] = Field(default=None, description="粉丝勋章颜色")
    medal_color_end: Optional[int] = Field(default=None, description="粉丝勋章颜色")
    medal_color_border: Optional[int] = Field(default=None, description="粉丝勋章边框颜色")
    is_lighted: Optional[int] = Field(default=None, description="是否被点亮")
    light_status: Optional[int] = Field(default=None, description="光效状态")
    wearing_status: Optional[int] = Field(default=0, description="当前是否佩戴：0：未佩戴, 1：已佩戴")
    score: Optional[int] = Field(default=None, description="得分")


class FansMedal(BaseModel):
    show: Optional[bool] = Field(default=None, description="是否显示粉丝勋章")
    wear: Optional[bool] = Field(default=None, description="是否佩戴了粉丝勋章")
    medal: Optional[Medal] = Field(default=None, description="粉丝勋章信息")


class SysNotice(BaseModel):
    id: Optional[int] = Field(default=None, description="id")
    content: Optional[str] = Field(default="", description="显示文案")
    url: Optional[str] = Field(default="", description="跳转地址")
    notice_type: Optional[int] = Field(default=None, description="提示类型")
    icon: Optional[str] = Field(default="", description="前缀图标")
    text_color: Optional[str] = Field(default="", description="文字颜色")
    bg_color: Optional[str] = Field(default="", description="背景颜色")


class LiveRoomWatchedShow(BaseModel):
    switch: Optional[bool] = Field(default=None, description="？")
    num: Optional[int] = Field(default=None, description="total watched users")
    text_small: Optional[str] = Field(default="", description="小型文本")
    text_large: Optional[str] = Field(default="", description="大型文本")
    icon: Optional[str] = Field(default="", description="watched icon url")
    icon_location: Optional[str] = Field(default="", description="？")
    icon_web: Optional[str] = Field(default="", description="watched icon url")


class LiveRoom(BaseModel):
    roomStatus: Optional[int] = Field(default=0, description="直播间状态：0：无房间, 1：有房间")
    liveStatus: Optional[int] = Field(default=0, description="直播状态：0：未开播, 1：直播中")
    url: Optional[str] = Field(default="", description="直播间网页 url")
    title: Optional[str] = Field(default="", description="直播间标题")
    cover: Optional[str] = Field(default="", description="直播间封面 url")
    watched_show: Optional[LiveRoomWatchedShow] = Field(default=None, description="观看信息")
    roomid: Optional[int] = Field(default=None, description="直播间 id")
    roundStatus: Optional[int] = Field(default=0, description="轮播状态：0：未轮播, 1：轮播")
    broadcast_type: Optional[int] = Field(default=None, description="广播类型")


class School(BaseModel):
    name: Optional[str] = Field(default="", description="就读大学名称，没有则为空")


class Profession(BaseModel):
    name: Optional[str] = Field(default="", description="资质名称")
    department: Optional[str] = Field(default="", description="职位")
    title: Optional[str] = Field(default="", description="所属机构")
    is_show: Optional[int] = Field(default=0, description="是否显示：0：不显示, 1：显示")


class UserHonourInfo(BaseModel):
    mid: Optional[int] = Field(default=0, description="用户mid")
    colour: Optional[str] = Field(default=None, description="颜色")
    tags: Optional[List[str]] = Field(default_factory=list, description="个人标签")


class Series(BaseModel):
    user_upgrade_status: Optional[int] = Field(default=None, description="用户升级状态")
    show_upgrade_window: Optional[bool] = Field(default=None, description="是否显示升级窗口")


class ShowInfo(BaseModel):
    show: Optional[bool] = Field(default=None, description="是否开通了充电")
    state: Optional[int] = Field(default=-1, description="状态：-1：未开通, 1：已开通")
    title: Optional[str] = Field(default="", description="标题")
    icon: Optional[str] = Field(default="", description="图标")
    jump_url: Optional[str] = Field(default="", description="跳转链接")


class Elec(BaseModel):
    show_info: Optional[ShowInfo] = Field(default=None, description="充电信息")


class Contract(BaseModel):
    is_display: Optional[bool] = Field(default=True, description="在页面中未使用此字段")
    is_follow_display: Optional[bool] = Field(default=True, description="是否在显示老粉计划")


class AccInfo(BaseModel):
    mid: Optional[int] = Field(default=None, description="mid")
    name: Optional[str] = Field(default="", description="昵称")
    sex: Optional[str] = Field(default="", description="性别：男/女/保密")
    face: Optional[str] = Field(default="", description="头像链接")
    face_nft: Optional[int] = Field(default=0, description="是否为 NFT 头像：0：不是, 1：是")
    face_nft_type: Optional[int] = Field(default=None, description="NFT 头像类型")
    sign: Optional[str] = Field(default="", description="签名")
    rank: Optional[int] = Field(default=None, description="用户权限等级")
    level: Optional[int] = Field(default=None, description="当前等级：0-6 级")
    jointime: Optional[int] = Field(default=0, description="注册时间，此接口返回恒为0")
    moral: Optional[int] = Field(default=0, description="节操值，此接口返回恒为0")
    silence: Optional[int] = Field(default=0, description="封禁状态：0：正常, 1：被封")
    coins: Optional[float] = Field(default=0, description="硬币数，默认为0")
    fans_badge: Optional[bool] = Field(default=False, description="是否具有粉丝勋章")
    fans_medal: Optional[FansMedal] = Field(default=None, description="粉丝勋章信息")
    official: Optional[Official] = Field(default=None, description="认证信息")
    vip: Optional[Vip] = Field(default=None, description="会员信息")
    pendant: Optional[Pendant] = Field(default=None, description="头像框信息")
    nameplate: Optional[Nameplate] = Field(default=None, description="勋章信息")
    user_honour_info: Optional[UserHonourInfo] = Field(default=None, description="用户荣誉信息")
    is_followed: Optional[bool] = Field(default=False, description="是否关注此用户")
    top_photo: Optional[str] = Field(default="", description="主页头图链接")
    theme: Optional[Dict[str, Any]] = Field(default=None, description="主题信息")
    sys_notice: Optional[SysNotice] = Field(default=None, description="系统通知")
    live_room: Optional[LiveRoom] = Field(default=None, description="直播间信息")
    birthday: Optional[str] = Field(default="", description="生日：MM-DD")
    school: Optional[School] = Field(default=None, description="学校")
    profession: Optional[Profession] = Field(default=None, description="专业资质信息")
    tags: Optional[List[str]] = Field(default_factory=list, description="个人标签")
    series: Optional[Series] = Field(default=None, description="用户系列信息")
    is_senior_member: Optional[int] = Field(default=0, description="是否为硬核会员：0：否, 1：是")
    mcn_info: Optional[Dict[str, Any]] = Field(default=None, description="MCN信息")
    gaia_res_type: Optional[int] = Field(default=None, description="Gaia资源类型")
    gaia_data: Optional[Dict[str, Any]] = Field(default=None, description="Gaia数据")
    is_risk: Optional[bool] = Field(default=None, description="风险状态")
    elec: Optional[Elec] = Field(default=None, description="充电信息")
    contract: Optional[Contract] = Field(default=None, description="老粉计划显示状态")


class GetAccInfoRes(BaseResponse):
    data: Optional[AccInfo] = Field(None)

