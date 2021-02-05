import json
import re
from struct import pack
from typing import Tuple, Awaitable

from aiohttp import WSMessage

from danmu_cli.base import BaseWebsocketProvider

color_tab = {
    '2': '1e87f0',
    '3': '7ac84b',
    '4': 'ff7f00',
    '6': 'ff69b4',
    '5': '9b39f4',
    '1': 'ff0000'
}


class DouyuService:
    heartbeat = b'\x14\x00\x00\x00\x14\x00\x00\x00\xb1\x02\x00\x00\x74\x79\x70\x65\x40\x3d\x6d\x72\x6b\x6c\x2f\x00'

    @staticmethod
    async def get_ws_info(roomid):
        reg_datas = []
        data = f'type@=loginreq/roomid@={roomid}/'
        s = pack('i', 9 + len(data)) * 2
        s += b'\xb1\x02\x00\x00'  # 689
        s += data.encode('ascii') + b'\x00'
        reg_datas.append(s)
        data = f'type@=joingroup/rid@={roomid}/gid@=-9999/'
        s = pack('i', 9 + len(data)) * 2
        s += b'\xb1\x02\x00\x00'  # 689
        s += data.encode('ascii') + b'\x00'
        reg_datas.append(s)
        return 'wss://danmuproxy.douyu.com:8506/', reg_datas, DouyuService.heartbeat

    @staticmethod
    def decode_msg(data):
        msgs = []
        for msg in re.findall(b'(type@=.*?)\x00', data):
            try:
                msg = msg.replace(b'@=', b'":"').replace(b'/', b'","')
                msg = msg.replace(b'@A', b'@').replace(b'@S', b'/')
                msg = json.loads((b'{"' + msg[:-2] + b'}').decode('utf8', 'ignore'))
                msg['name'] = msg.get('nn', '')
                msg['content'] = msg.get('txt', '')
                msg['msg_type'] = {'dgb': 'gift', 'chatmsg': 'danmaku',
                                   'uenter': 'enter'}.get(msg['type'], 'other')
                msg['color'] = color_tab.get(msg.get('col', '-1'), 'ffffff')
                msgs.append(msg)
            except Exception as e:
                pass
        return msgs


class DouyuProvider(BaseWebsocketProvider):
    async def received(self, message: WSMessage):
        print(DouyuService.decode_msg(message.data))

    async def ws_info(self) -> Awaitable[Tuple[str, list, bytes]]:
        return await DouyuService.get_ws_info(self.roomid)
