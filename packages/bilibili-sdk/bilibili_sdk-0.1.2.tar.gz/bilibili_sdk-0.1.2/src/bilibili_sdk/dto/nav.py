from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from .base import BaseResponse

class LevelInfo(BaseModel):
    current_level: Optional[int] = Field(default=None, description="当前等级")
    current_min: Optional[int] = Field(default=None, description="当前等级经验最低值")
    current_exp: Optional[int] = Field(default=None, description="当前经验")
    next_exp: Optional[Union[str, int]] = Field(default=None, description="升级下一等级需达到的经验")

class Official(BaseModel):
    role: Optional[int] = Field(default=None, description="认证类型")
    title: Optional[str] = Field(default="", description="认证信息，无为空")
    desc: Optional[str] = Field(default="", description="认证备注，无为空")
    type: Optional[int] = Field(default=-1, description="是否认证：-1：无, 0：认证")

class OfficialVerify(BaseModel):
    type: Optional[int] = Field(default=-1, description="是否认证：-1：无, 0：认证")
    desc: Optional[str] = Field(default="", description="认证信息，无为空")

class Pendant(BaseModel):
    pid: Optional[int] = Field(default=None, description="挂件id")
    name: Optional[str] = Field(default="", description="挂件名称")
    image: Optional[str] = Field(default="", description="挂件图片url")
    expire: Optional[int] = Field(default=None, description="过期时间，具体用途不明")

class VipLabel(BaseModel):
    path: Optional[str] = Field(default="", description="（？）")
    text: Optional[str] = Field(default="", description="会员名称")
    label_theme: Optional[str] = Field(default="", description="会员标签")

class Wallet(BaseModel):
    mid: Optional[int] = Field(default=None, description="登录用户mid")
    bcoin_balance: Optional[int] = Field(default=0, description="拥有B币数")
    coupon_balance: Optional[int] = Field(default=0, description="每月奖励B币数")
    coupon_due_time: Optional[int] = Field(default=None, description="（？）")

class WbiImg(BaseModel):
    img_url: Optional[str] = Field(default="", description="Wbi 签名参数 imgKey的伪装 url")
    sub_url: Optional[str] = Field(default="", description="Wbi 签名参数 subKey的伪装 url")

class NavInfo(BaseModel):
    isLogin: Optional[bool] = Field(default=False, description="是否已登录：false：未登录, true：已登录")
    email_verified: Optional[int] = Field(default=0, description="是否验证邮箱地址：0：未验证, 1：已验证")
    face: Optional[str] = Field(default="", description="用户头像 url")
    level_info: Optional[LevelInfo] = Field(default=None, description="等级信息")
    mid: Optional[int] = Field(default=None, description="用户 mid")
    mobile_verified: Optional[int] = Field(default=0, description="是否验证手机号：0：未验证, 1：已验证")
    money: Optional[float] = Field(default=0, description="拥有硬币数")
    moral: Optional[int] = Field(default=0, description="当前节操值，上限为70")
    official: Optional[Official] = Field(default=None, description="认证信息")
    officialVerify: Optional[OfficialVerify] = Field(default=None, description="认证信息 2")
    pendant: Optional[Pendant] = Field(default=None, description="头像框信息")
    scores: Optional[int] = Field(default=None, description="（？）")
    uname: Optional[str] = Field(default="", description="用户昵称")
    vipDueDate: Optional[int] = Field(default=0, description="会员到期时间，毫秒时间戳")
    vipStatus: Optional[int] = Field(default=0, description="会员开通状态：0：无, 1：有")
    vipType: Optional[int] = Field(default=0, description="会员类型：0：无, 1：月度大会员, 2：年度及以上大会员")
    vip_pay_type: Optional[int] = Field(default=0, description="会员开通状态：0：无, 1：有")
    vip_theme_type: Optional[int] = Field(default=None, description="（？）")
    vip_label: Optional[VipLabel] = Field(default=None, description="会员标签")
    vip_avatar_subscript: Optional[int] = Field(default=0, description="是否显示会员图标：0：不显示, 1：显示")
    vip_nickname_color: Optional[str] = Field(default="", description="会员昵称颜色，颜色码")
    wallet: Optional[Wallet] = Field(default=None, description="B币钱包信息")
    has_shop: Optional[bool] = Field(default=False, description="是否拥有推广商品：false：无, true：有")
    shop_url: Optional[str] = Field(default="", description="商品推广页面 url")
    allowance_count: Optional[int] = Field(default=None, description="（？）")
    answer_status: Optional[int] = Field(default=None, description="（？）")
    is_senior_member: Optional[int] = Field(default=0, description="是否硬核会员：0：非硬核会员, 1：硬核会员")
    wbi_img: Optional[WbiImg] = Field(default=None, description="Wbi 签名实时口令，用户未登录也存在")
    is_jury: Optional[bool] = Field(default=False, description="是否风纪委员：true：风纪委员, false：非风纪委员")

class GetWebInferfaceNavRes(BaseResponse):
    data: Optional[NavInfo] = Field(None)
