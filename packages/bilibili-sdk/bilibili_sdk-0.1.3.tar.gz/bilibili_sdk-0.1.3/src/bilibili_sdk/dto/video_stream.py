#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:
# Description:
'''
## qn视频清晰度标识

注：该值在 DASH 格式下无效，因为 DASH 格式会取到所有分辨率的流地址

又注: B站对于新的视频更新了播放设置, 较高分辨率均采用 DASH, 较低分辨率与老视频还保留了 MP4, 这导致较新视频无法获取 MP4 格式的高分辨率视频, 参见 [#606](https://github.com/SocialSisterYi/bilibili-API-collect/issues/606) 或 [cv949156](https://www.bilibili.com/read/cv949156/)

| 值   | 含义           | 备注                                                         |
| ---- | -------------- | ------------------------------------------------------------ |
| 6    | 240P 极速      | 仅 MP4 格式支持<br />仅`platform=html5`时有效                |
| 16   | 360P 流畅      |                                                              |
| 32   | 480P 清晰      |                                                              |
| 64   | 720P 高清      | WEB 端默认值<br />B站前端需要登录才能选择，但是直接发送请求可以不登录就拿到 720P 的取流地址<br />**无 720P 时则为 720P60** |
| 74   | 720P60 高帧率  | 登录认证                                                     |
| 80   | 1080P 高清     | TV 端与 APP 端默认值<br />登录认证                           |
| 112  | 1080P+ 高码率  | 大会员认证                                                   |
| 116  | 1080P60 高帧率 | 大会员认证                                                   |
| 120  | 4K 超清        | 需要`fnval&128=128`且`fourk=1`<br />大会员认证               |
| 125  | HDR 真彩色     | 仅支持 DASH 格式<br />需要`fnval&64=64`<br />大会员认证      |
| 126  | 杜比视界       | 仅支持 DASH 格式<br />需要`fnval&512=512`<br />大会员认证    |
| 127  | 8K 超高清      | 仅支持 DASH 格式<br />需要`fnval&1024=1024`<br />大会员认证  |

例如：请求 1080P+ 的视频，则`qn=112`

## 视频伴音音质代码accept_description

| 值    | 含义 |
| ----- | ---- |
| 30216 | 64K  |
| 30232 | 132K |
| 30280 | 192K |
| 30250 | 杜比全景声 |
| 30251 | Hi-Res无损 |


'''
from typing import List, Optional, Dict
from pydantic import Field, BaseModel
from bilibili_sdk.enums.archive import ArchiveStatus
from .base import BaseListReq, BaseResponse

class GetPlayerUrlReq(BaseModel):
    avid: int = Field(0, title='avid')
    bvid: str = Field("", title="视频id")
    cid: int = Field(title="单个视频 id")
    qn: int = Field(80, title="清晰度",
        description='未登录默认 32（480P），登录后默认 64（720P）DASH 格式时无效,含义见 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md')
    fnval: int = Field(1, title="视频流格式标识",
        description='默认值为1（MP4 格式）含义见 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md#fnval%E8%A7%86%E9%A2%91%E6%B5%81%E6%A0%BC%E5%BC%8F%E6%A0%87%E8%AF%86')
    fnver: int = Field(0, title='视频流版本标识', description='目前该值恒为 0')
    fourk: int = Field(0, title='是否允许 4K 视频', description='画质最高 1080P：0（默认）画质最高 4K：1')
    platform: str = Field("html5", title='平台')
    high_quality: int = Field(1, title='是否高画质', description='platform=html5时，此值为1可使画质为1080p')

class Durl(BaseModel):
    order: int = Field(0, title='视频分段序号', description='某些视频会分为多个片段（从1顺序增长')
    length: int = Field(0, title='视频长度', description='单位为毫秒')
    size: int = Field(0, title='视频大小', description='单位为Byte')
    url: str = Field("", title='默认流URL', description='注意 unicode 转义符,有效时间为120min')
    backup_url: Optional[List[str]] = Field([], title='备用视频流')

class SegmentBase(BaseModel):
    initialization: Optional[str] = Field(
        None,
        title="初始化范围",
        description="ftyp (file type) box 加上 moov box 在 m4s 文件中的范围（单位为 bytes）。例如：0-821 表示开头 820 个字节。"
    )
    index_range: Optional[str] = Field(
        None,
        title="索引范围",
        description="sidx (segment index) box 在 m4s 文件中的范围（单位为 bytes）。例如：822-1309。sidx 的核心是一个数组，记录了各关键帧的时间戳及其在文件中的位置，其作用是索引（拖进度条）。"
    )

class DashItem(BaseModel):
    id: Optional[int] = Field(None, title="音视频清晰度代码", description="参考 qn视频清晰度标识 视频伴音音质代码", alias="id")
    base_url: Optional[str] = Field(None, title="默认流 URL", description="注意 unicode 转义符")
    backup_url: Optional[List[str]] = Field(None, title="备用流 URL",)
    bandwidth: Optional[int] = Field(None, title="所需最低带宽", description="单位为 Byte", alias="bandwidth")
    mime_type: Optional[str] = Field(None, title="格式 mimetype 类型")
    codecs: Optional[str] = Field(None, title="编码/音频类型", description="eg：avc1.640032", alias="codecs")
    width: Optional[int] = Field(None, title="视频宽度", description="单位为像素，仅视频流存在该字段", alias="width")
    height: Optional[int] = Field(None, title="视频高度", description="单位为像素，仅视频流存在该字段", alias="height")
    frame_rate: Optional[str] = Field(None, title="视频帧率", description="仅视频流存在该字段")
    sar: Optional[str] = Field(None, title="Sample Aspect Ratio（单个像素的宽高比）", description="音频流该恒值为空", alias="sar")
    start_with_sap: Optional[int] = Field(None, title="Stream Access Point（流媒体访问位点）", description="音频流该值恒为空")
    segment_base: Optional[SegmentBase] = Field(None, title="见下表 url 对应 m4s 文件中，头部的位置", description="音频流该值恒为空")
    codecid: Optional[int] = Field(None, title="码流编码标识代码", description="含义见 上表 音频流该值恒为0", alias="codecid")

class Dolby(BaseModel):
    type: Optional[int] = Field(None, title="杜比音效类型", description="1：普通杜比音效；2：全景杜比音效")
    audio: Optional[List[DashItem]] = Field(None, title="杜比伴音流列表", description="同上文 DASH 流中 video 及 audio 数组中的对象")

class Flac(BaseModel):
    display: Optional[bool] = Field(None, title="是否在播放器显示切换 Hi-Res 无损音轨按钮")
    audio: Optional[DashItem] = Field(None, title="音频流信息", description="同上文 DASH 流中 video 及 audio 数组中的对象")

class Dash(BaseModel):
    duration: Optional[int] = Field(None, title="视频长度", description="视频长度，单位为秒", alias="duration")
    min_buffer_time: Optional[float] = Field(None, title="最小缓冲时间", description="1.5？")
    video: Optional[List[DashItem]] = Field(None, title="视频流信息", description="视频流信息", alias="video")
    audio: Optional[List[DashItem]] = Field(None, title="伴音流信息", description="伴音流信息，当视频没有音轨时，此项为 null", alias="audio")
    dolby: Optional[Dolby] = Field(None, title="杜比全景声伴音信息", description="杜比全景声伴音信息", alias="dolby")
    flac: Optional[Flac] = Field(None, title="无损音轨伴音信息", description="无损音轨伴音信息，当视频没有无损音轨时，此项为 null", alias="flac")

class SupportFormat(BaseModel):
    quality: Optional[int] = Field(None, title="视频清晰度代码", description="含义见 qn视频清晰度标识")
    format: Optional[str] = Field(None, title="视频格式")
    new_description: Optional[str] = Field(None, title="格式描述")
    display_desc: Optional[str] = Field(None, title="格式描述")
    superscript: Optional[str] = Field(None, title="(?)")
    codecs: Optional[List[str]] = Field(None, title="可用编码格式列表")

class PlayerUrl(BaseModel):
    from_: Optional[str] = Field(None, title="来源", description="local？", alias="from")
    result: Optional[str] = Field(None, title="结果", description="suee？", alias="result")
    message: Optional[str] = Field(None, title="消息", description="空？", alias="message")
    quality: Optional[int] = Field(None, title="清晰度标识", description="含义见 上表", alias="quality")
    format: Optional[str] = Field(None, title="视频格式", description="mp4/flv", alias="format")
    timelength: Optional[int] = Field(None, title="视频长度", description="单位为毫秒，不同分辨率 / 格式可能有略微差异", alias="timelength")
    accept_format: Optional[str] = Field(None, title="支持的全部格式", description="每项用,分隔", alias="accept_format")
    accept_description: Optional[List[str]] = Field(None, title="支持的清晰度列表（文字说明）", alias="accept_description")
    accept_quality: Optional[List[int]] = Field(None, title="支持的清晰度列表（代码）", description="含义见 上表", alias="accept_quality")
    video_codecid: Optional[int] = Field(None, title="默认选择视频流的编码id", description="含义见 上表", alias="video_codecid")
    seek_param: Optional[str] = Field(None, title="seek 参数", description="start？", alias="seek_param")
    seek_type: Optional[str] = Field(None, title="seek 类型", description="offset（DASH / FLV）？second（MP4）？", alias="seek_type")
    durl: Optional[List[Durl]] = Field(None, title="视频分段流信息", description="注：仅 FLV / MP4 格式存在此字段", alias="durl")
    dash: Optional[Dash] = Field(None, title="DASH 流信息", description="注：仅 DASH 格式存在此字段", alias="dash")
    support_formats: Optional[List[SupportFormat]] = Field(None, title="支持格式的详细信息", alias="support_formats")
    high_format: Optional[str] = Field(None, title="（？）", alias="high_format")
    last_play_time: Optional[int] = Field(None, title="上次播放进度", description="毫秒值", alias="last_play_time")
    last_play_cid: Optional[int] = Field(None, title="上次播放分P的 cid", alias="last_play_cid")

    @property
    def default_url(self):
        """使用默认地址"""
        if not self.durl:
            return ""
        return self.durl[0].url

    @property
    def default_durl(self) -> Durl:
        """使用默认地址对象"""
        if not self.durl:
            return None
        return self.durl[0]

class GetPlayerUrlRes(BaseResponse):
    data: Optional[PlayerUrl] = Field(default=None)
