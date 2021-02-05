from danmu_cli.base import BasePresenter, BaseDanmu


class DefaultPresenter(BasePresenter):
    def present(self, danmu: BaseDanmu):
        print(danmu)
