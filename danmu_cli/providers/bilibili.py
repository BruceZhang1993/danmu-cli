from danmu_cli.base import BaseProvider, BaseDanmu, BaseType
from danmu_cli.providers.bilibili_content.service import BilibiliLiveDanmuService, DanmuData


class BilibiliDanmu(BaseDanmu):
    pass


class BilibiliProvider(BaseProvider):
    service: BilibiliLiveDanmuService

    def setup(self):
        self.service = BilibiliLiveDanmuService()
        self.service.register_callback(self.callback)

    def callback(self, danmu: DanmuData):
        if danmu.msg_type == BilibiliLiveDanmuService.TYPE_DANMUKU:
            d = BilibiliDanmu()
            d.type = BaseType.danmuku
            d.message = f'{danmu.name}: {danmu.content}'
            self.send(d)

    async def run(self):
        await self.service.ws_connect(3573632)

    def teardown(self):
        self.service.unregister_callback(self.callback)
