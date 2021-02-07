import asyncio
from abc import ABCMeta, abstractmethod
from collections import Awaitable
from enum import Enum
from typing import Optional, Tuple, Union
from pydantic import BaseModel

from aiohttp import WSMessage

from danmu_cli.service import WebsocketDanmuService


class BaseType(Enum):
    danmuku = 1  # 普通弹幕
    enter = 2  # 用户入场
    broadcast = 3  # 广播通知
    gift = 4  # 礼物
    other = 5  # 其他


class BaseDanmu(BaseModel):
    @property
    @abstractmethod
    def message(self):
        pass

    @property
    @abstractmethod
    def type(self):
        pass

    @property
    @abstractmethod
    def username(self):
        pass


class BasePresenter(metaclass=ABCMeta):
    def setup(self):
        pass

    @abstractmethod
    def present(self, danmu: BaseDanmu):
        pass

    def teardown(self):
        pass


class BaseProvider(metaclass=ABCMeta):
    def __init__(self):
        self.presenter: Optional[BasePresenter] = None
        self.roomid: Optional[str] = None

    def setup(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def send(self, danmu: BaseDanmu):
        if self.presenter is not None:
            self.presenter.present(danmu)

    def teardown(self):
        pass


class BaseWebsocketProvider(BaseProvider, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.service: Optional[WebsocketDanmuService] = None

    async def run(self):
        if asyncio.iscoroutinefunction(self.ws_info):
            ws_address, payloads, hb = await self.ws_info()
        else:
            loop = asyncio.get_event_loop()
            ws_address, payloads, hb = await loop.run_in_executor(None, self.ws_info)
        if ws_address == '':
            return
        self.service = WebsocketDanmuService(ws_address, payloads, hb, 30, self.received)
        await self.service.connect()

    @abstractmethod
    async def received(self, data: WSMessage):
        pass

    @abstractmethod
    def ws_info(self) -> Union[Tuple[str, list, bytes], Awaitable[Tuple[str, list, bytes]]]:
        pass

    async def teardown(self):
        if self.service is not None:
            await self.service.stop()
