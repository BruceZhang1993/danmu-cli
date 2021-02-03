from danmu_cli.base import BasePresenter, BaseDanmu


class PlainPresenter(BasePresenter):
    def present(self, danmu: BaseDanmu):
        print(danmu)
