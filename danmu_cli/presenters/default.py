from danmu_cli.base import BasePresenter, BaseDanmu, BaseType


class DefaultPresenter(BasePresenter):
    def present(self, danmu: BaseDanmu):
        if danmu.type == BaseType.danmuku:
            print(f'{danmu.username} => {danmu.message}')
        else:
            print(f'Other => {danmu}')
