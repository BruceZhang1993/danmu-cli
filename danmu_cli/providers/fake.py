import random
import time

from danmu_cli.base import BaseProvider, BaseDanmu, BaseType


WORDS = ['apple', 'orange', 'banana', 'juice', 'hotdog', 'hamberger', 'noodles']


class FakeDanmu(BaseDanmu):
    pass


class FakeProvider(BaseProvider):
    def run(self):
        for _ in range(0, 10):
            time.sleep(1)
            danmu = FakeDanmu()
            danmu.type = BaseType.danmuku
            danmu.message = random.choice(WORDS)
            self.send(danmu)
