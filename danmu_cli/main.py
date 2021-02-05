import asyncio
import signal
import sys
from typing import Type
from urllib.parse import urlparse

import click

from danmu_cli.base import BasePresenter, BaseProvider
from danmu_cli.presenters import get_presenter
from danmu_cli.providers import get_provider

presenter_type: Type[BasePresenter]
provider_type: Type[BaseProvider]
presenter_obj: BasePresenter
provider_obj: BaseProvider


def initialize(roomid: str, provider: str, presenter: str = 'default'):
    global presenter_type, provider_type, presenter_obj, provider_obj
    presenter_type = get_presenter(presenter)
    provider_type = get_provider(provider)
    presenter_obj = presenter_type()
    presenter_obj.setup()
    provider_obj = provider_type()
    provider_obj.presenter = presenter_obj
    provider_obj.roomid = roomid
    provider_obj.setup()


async def running():
    loop = asyncio.get_event_loop()
    if asyncio.iscoroutinefunction(provider_obj.run):
        await provider_obj.run()
    else:
        await loop.run_in_executor(None, provider_obj.run)
    if asyncio.iscoroutinefunction(provider_obj.teardown):
        await provider_obj.teardown()
    else:
        await loop.run_in_executor(None, provider_obj.teardown)
    presenter_obj.teardown()


async def gracefully_quit():
    print(f'\nSignal received. Gracefully quitting...')
    loop = asyncio.get_event_loop()
    if asyncio.iscoroutinefunction(provider_obj.teardown):
        await provider_obj.teardown()
    else:
        await loop.run_in_executor(None, provider_obj.teardown)
    presenter_obj.teardown()


@click.command()
@click.argument('roomid', required=True)
@click.option('--provider', help='Provider name', type=click.Choice(['bilibili', 'douyu', 'huya']))
@click.option('--presenter', help='Presenter name', type=click.Choice(['default']), default='default')
def main(roomid: str, provider: str, presenter: str = 'default'):
    if roomid.startswith('http'):
        parsed = urlparse(roomid)
        host = parsed.netloc
        path = parsed.path
        if host.endswith('bilibili.com'):
            provider = 'bilibili'
            roomid = path.split('/')[-1]
        elif host.endswith('douyu.com'):
            provider = 'douyu'
            roomid = path.split('/')[-1]
        elif host.endswith('huya.com'):
            provider = 'huya'
            roomid = path.split('/')[-1]
    if provider is None:
        click.echo('cannot find provider', err=True)
        sys.exit(1)
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.ensure_future(gracefully_quit()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.ensure_future(gracefully_quit()))
    initialize(roomid, provider, presenter)
    loop.run_until_complete(running())
