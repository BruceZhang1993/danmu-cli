import asyncio
from asyncio import Future
from contextlib import suppress
from typing import Optional, Callable, Awaitable

from aiohttp import ClientSession, ClientWebSocketResponse, WSMessage


class WebsocketDanmuService:
    def __init__(self, ws_address: str, payload: bytes, hb: bytes, interval: int,
                 callback: Callable[[WSMessage], Optional[Awaitable]]):
        self.ws: Optional[ClientWebSocketResponse] = None
        self.session = ClientSession()
        self.ws_address = ws_address
        self.payload = payload
        self.hb = hb
        self.interval = interval
        self.heartbeat_task: Optional['Future'] = None
        self.cb = callback

    async def connect(self):
        async with self.session.ws_connect(self.ws_address) as ws:
            self.ws = ws
            await self.running()

    async def send_heartbeat_once(self):
        await self.ws.send_bytes(self.hb)

    async def send_heartbeat(self):
        while True:
            await asyncio.sleep(self.interval)
            await self.send_heartbeat_once()

    async def running(self):
        await self.ws.send_bytes(self.payload)
        self.heartbeat_task = asyncio.ensure_future(self.send_heartbeat())
        async for msg in self.ws:
            msg: WSMessage
            if asyncio.iscoroutinefunction(self.cb):
                await self.cb(msg)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.cb, msg)

    async def stop(self):
        self.heartbeat_task.cancel()
        with suppress(asyncio.CancelledError):
            await self.heartbeat_task
        await self.ws.close()
        await self.session.close()
