from typing import Tuple, Awaitable, Union, Any

from aiohttp import WSMessage

from danmu_cli.base import BaseDanmu, BaseWebsocketProvider
from danmu_cli.providers.bilibili_content.service import BilibiliLiveDanmuService


class BilibiliDanmu(BaseDanmu):
    msg_type: str
    content: Union[bytes, dict, Any]

    @property
    def message(self):
        pass

    @property
    def type(self):
        pass

    @property
    def username(self):
        pass


class BilibiliProvider(BaseWebsocketProvider):
    bservice: BilibiliLiveDanmuService

    def setup(self):
        self.bservice = BilibiliLiveDanmuService()

    async def received(self, message: WSMessage):
        for msg in self.bservice.decode_msg(message.data):
            print(msg)

    async def ws_info(self) -> Awaitable[Tuple[str, list, bytes]]:
        result = await self.bservice.get_ws_info(self.roomid)
        await self.bservice.session.close()
        return result
