import datetime
from typing import List, Any, Optional, Union

from pydantic import BaseModel, Field


class DanmuKeyData(BaseModel):
    class DanmuHost(BaseModel):
        host: str
        port: int
        wss_port: int
        ws_port: int

    group: str
    business_id: int
    refresh_row_factor: float
    refresh_rate: int
    max_delay: int
    token: str
    host_list: List[DanmuHost]


class BaseResponseV2(BaseModel):
    code: int
    message: str
    data: Any


class DanmuKeyResponse(BaseResponseV2):
    ttl: int
    data: DanmuKeyData


class RoomInitData(BaseModel):
    room_id: int
    short_id: int
    uid: int
    need_p2p: bool
    is_hidden: bool
    is_locked: bool
    is_portrait: bool
    live_status: bool
    hidden_till: int
    lock_till: int
    encrypted: bool
    pwd_verified: bool
    live_time: int
    room_shield: int
    is_sp: bool
    special_type: int


class RoomInitResponse(BaseResponseV2):
    data: RoomInitData


class SendGiftData(BaseModel):
    draw: int
    gold: int
    silver: int
    num: int
    total_coin: int
    effect: int
    broadcast_id: int
    crit_prob: int
    guard_level: int
    rcost: int
    uid: int
    timestamp: datetime.datetime
    gift_type: int = Field(alias='giftType')
    price: int
    action: str
    coin_type: str
    uname: str
    face: str
    gift_name: str = Field(alias='giftName')


class WelcomeData(BaseModel):
    uid: int
    uname: str
    is_admin: bool
    svip: bool
    vip: bool
    mock_effect: Optional[int]


class RoomBannerData(BaseModel):
    rank_status: bool
    task_status: bool
    rank_default: int
    rank_info: dict
    task_info: dict


class RoomRealTimeMessageUpdateData(BaseModel):
    roomid: int
    fans: int
    red_notice: int
    fans_club: int


class DanmuContent(BaseModel):
    cmd: str
    type: Optional[int]
    id: Optional[int]
    data: Union[RoomRealTimeMessageUpdateData, WelcomeData, SendGiftData, Any, None]


class DanmuData(BaseModel):
    msg_type: str
    name: Optional[str]
    type: Optional[int]
    roomid: Optional[int]
    raw: Optional[dict]
    content: Union[DanmuContent, str, bytes]
