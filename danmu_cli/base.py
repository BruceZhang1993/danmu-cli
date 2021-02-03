from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Optional


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

    def run(self):
        pass

    def send(self, danmu: BaseDanmu):
        if self.presenter is not None:
            self.presenter.present(danmu)

    def teardown(self):
        pass
