import asyncio
from abc import ABCMeta, abstractmethod
from collections import Awaitable
from enum import Enum
from typing import Optional, Tuple, Union

from aiohttp import WSMessage

from danmu_cli.service import WebsocketDanmuService


class BaseType(Enum):
    danmuku = 1  # 普通弹幕
    enter = 2  # 用户入场
    broadcast = 3  # 广播通知
    gift = 4  # 礼物
    other = 5  # 其他


class BaseDanmu(metaclass=ABCMeta):
    def __init__(self):
        self.type: Optional[BaseType] = None
        self.message: Optional[str] = None

    def __str__(self):
        return f'{__class__.__name__}: [{self.type.name}] {self.message}'


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
    async def run(self):
        if asyncio.iscoroutinefunction(self.ws_info):
            ws_address, payload, hb = await self.ws_info()
        else:
            loop = asyncio.get_event_loop()
            ws_address, payload, hb = await loop.run_in_executor(None, self.ws_info)
        self.service = WebsocketDanmuService(ws_address, payload, hb, 30, self.received)
        await self.service.connect()

    @abstractmethod
    async def received(self, data: WSMessage):
        pass

    @abstractmethod
    def ws_info(self) -> Union[Tuple[str, bytes, bytes], Awaitable[Tuple[str, bytes, bytes]]]:
        pass

    async def teardown(self):
        await self.service.stop()
