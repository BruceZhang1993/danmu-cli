import asyncio
import signal
from typing import Type

from danmu_cli.base import BasePresenter, BaseProvider
from danmu_cli.presenters import get_presenter
from danmu_cli.providers import get_provider

presenter_type: Type[BasePresenter]
provider_type: Type[BaseProvider]
presenter: BasePresenter
provider: BaseProvider


def initialize():
    global presenter_type, provider_type, presenter, provider
    presenter_type = get_presenter('plain')
    provider_type = get_provider('bilibili')
    presenter = presenter_type()
    presenter.setup()
    provider = provider_type()
    provider.presenter = presenter
    provider.setup()


async def running():
    loop = asyncio.get_event_loop()
    if asyncio.iscoroutinefunction(provider.run):
        await provider.run()
    else:
        await loop.run_in_executor(None, provider.run)
    if asyncio.iscoroutinefunction(provider.teardown):
        await provider.teardown()
    else:
        await loop.run_in_executor(None, provider.teardown)
    presenter.teardown()


async def gracefully_quit():
    print(f'Signal received. Gracefully quitting...')
    loop = asyncio.get_event_loop()
    if asyncio.iscoroutinefunction(provider.teardown):
        await provider.teardown()
    else:
        await loop.run_in_executor(None, provider.teardown)
    presenter.teardown()


def main():
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.ensure_future(gracefully_quit()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.ensure_future(gracefully_quit()))
    initialize()
    loop.run_until_complete(running())
