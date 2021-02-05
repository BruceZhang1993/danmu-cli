import asyncio

from danmu_cli.base import BaseProvider, BaseDanmu, BaseType

WORDS = ['apple', 'orange', 'banana', 'juice', 'hotdog', 'hamberger', 'noodles']


class FakeDanmu(BaseDanmu):
    pass


class FakeProvider(BaseProvider):
    async def run(self):
        for _ in range(0, 10):
            await asyncio.sleep(1)
            danmu = FakeDanmu()
            self.send(danmu)
