import asyncio
import json
import zlib
from random import random
from struct import unpack
from threading import Timer

from aiohttp import WSMessage, WSMsgType, ClientSession

from .models import *


class BilibiliServiceException(Exception):
    pass


class BilibiliLiveDanmuService:
    # API 域名
    LIVE_API_HOST = 'api.live.bilibili.com'

    # 弹幕地址
    DANMU_WS = 'wss://broadcastlv.chat.bilibili.com/sub'

    # 操作类型
    TYPE_JOIN_ROOM = 7
    TYPE_HEARTBEAT = 2

    # 消息类型
    TYPE_DANMUKU = 'danmaku'
    TYPE_ENTER = 'enter'
    TYPE_BROADCAST = 'broadcast'
    TYPE_GIFT = 'gift'
    TYPE_OTHER = 'other'

    def __init__(self):
        super().__init__()
        self.ws = None
        self.timer: Optional[Timer] = None
        self.callbacks = set()
        self.external_callbacks = set()
        self.session = ClientSession()

    def register_callback(self, callback, external=True):
        if external:
            self.external_callbacks.add(callback)
        else:
            self.callbacks.add(callback)

    def unregister_callback(self, callback):
        try:
            self.callbacks.remove(callback)
            self.external_callbacks.remove(callback)
        except KeyError:
            pass
        if len(self.callbacks) == 0:
            if self.timer is not None:
                self.timer.cancel()
            asyncio.gather(self.ws.close())

    async def get_danmu_key(self, roomid) -> DanmuKeyData:
        params = {'id': roomid, 'type': 0}
        async with self.session.get(f'https://{self.LIVE_API_HOST}/xlive/web-room/v1/index/getDanmuInfo',
                                    params=params) as r:
            res = DanmuKeyResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
            return res.data

    @staticmethod
    def decode_msg(data):
        dm_list_compressed = []
        dm_list = []
        ops = []
        msgs = []
        while True:
            try:
                packet_len, header_len, ver, op, seq = unpack('!IHHII', data[0:16])
            except:
                break
            if len(data) < packet_len:
                break
            if ver == 1 or ver == 0:
                ops.append(op)
                dm_list.append(data[16:packet_len])
            elif ver == 2:
                dm_list_compressed.append(data[16:packet_len])
            if len(data) == packet_len:
                data = b''
                break
            else:
                data = data[packet_len:]
        for dm in dm_list_compressed:
            d = zlib.decompress(dm)
            while True:
                try:
                    packet_len, header_len, ver, op, seq = unpack('!IHHII', d[0:16])
                except:
                    break
                if len(d) < packet_len:
                    break
                ops.append(op)
                dm_list.append(d[16:packet_len])
                if len(d) == packet_len:
                    d = b''
                    break
                else:
                    d = d[packet_len:]
        for i, d in enumerate(dm_list):
            try:
                msg = {}
                if ops[i] == 5:
                    j = json.loads(d)
                    msg['msg_type'] = {'SEND_GIFT': 'gift', 'DANMU_MSG': 'danmaku',
                                       'WELCOME': 'enter', 'NOTICE_MSG': 'broadcast'}.get(j.get('cmd'), 'other')
                    if msg['msg_type'] == 'danmaku':
                        msg['name'] = (j.get('info', ['', '', ['', '']])[2][1]
                                       or j.get('data', {}).get('uname', ''))
                        msg['content'] = j.get('info', ['', ''])[1]
                    elif msg['msg_type'] == 'broadcast':
                        msg['type'] = j.get('msg_type', 0)
                        msg['roomid'] = j.get('real_roomid', 0)
                        msg['content'] = j.get('msg_common', 'none')
                        msg['raw'] = j
                    else:
                        msg['content'] = j
                else:
                    msg = {'name': '', 'content': d, 'msg_type': 'other'}
                msgs.append(msg)
            except:
                pass
        return msgs

    @staticmethod
    def encode_payload(data, type_=TYPE_HEARTBEAT):
        payload = json.dumps(data, separators=(',', ':')).encode('ascii')
        payload_length = len(payload) + 16
        data = payload_length.to_bytes(4, byteorder='big')
        data += (16).to_bytes(2, byteorder='big')
        data += (1).to_bytes(2, byteorder='big')
        data += type_.to_bytes(4, byteorder='big')
        data += (1).to_bytes(4, byteorder='big')
        data += payload
        return data

    async def send_heatbeat(self):
        await self.ws.send_bytes(self.encode_payload('[object Object]'))

    async def room_init(self, roomid) -> RoomInitData:
        room_init_uri = f'https://{self.LIVE_API_HOST}/room/v1/Room/room_init'
        room_init_params = {'id': roomid}
        async with self.session.get(room_init_uri, params=room_init_params) as r:
            res = RoomInitResponse(**(await r.json()))
            if res.code != 0:
                raise BilibiliServiceException(res.message, res.code)
        return res.data

    async def get_ws_info(self, roomid):
        room_init_data = await self.room_init(roomid)
        token_data = await self.get_danmu_key(room_init_data.room_id)
        payload = {'uid': int(1e14 + 2e14 * random()), 'roomid': room_init_data.room_id, 'protover': 1,
                   'platform': 'web', 'clientver': '1.14.1', 'type': 2, 'key': token_data.token}
        return self.DANMU_WS, [self.encode_payload(payload, type_=self.TYPE_JOIN_ROOM)], self.encode_payload('[object Object]')
