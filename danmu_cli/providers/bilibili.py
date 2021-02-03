from typing import Tuple, Awaitable

from aiohttp import WSMessage

from danmu_cli.base import BaseDanmu, BaseWebsocketProvider
from danmu_cli.providers.bilibili_content.service import BilibiliLiveDanmuService


class BilibiliDanmu(BaseDanmu):
    pass


class BilibiliProvider(BaseWebsocketProvider):
    bservice: BilibiliLiveDanmuService

    def setup(self):
        self.bservice = BilibiliLiveDanmuService()

    async def received(self, message: WSMessage):
        print(self.bservice.decode_msg(message.data))

    async def ws_info(self) -> Awaitable[Tuple[str, bytes, bytes]]:
        result = await self.bservice.get_ws_info(466)
        await self.bservice.session.close()
        return result
