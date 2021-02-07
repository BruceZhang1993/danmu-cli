import asyncio
import signal
import sys
from typing import Type, Optional, Tuple
from urllib.parse import urlparse

import click
import pkg_resources

from danmu_cli.base import BasePresenter, BaseProvider
from danmu_cli.presenters import get_presenter
from danmu_cli.providers import get_provider
from . import __appname__, __appart__

__version__ = pkg_resources.get_distribution('danmu-cli').version

from .util import asynchronous_run

presenter_type: Type[BasePresenter]
provider_type: Type[BaseProvider]
presenter_obj: BasePresenter
provider_obj: BaseProvider


def initialize(roomid: str, provider: str, presenter: str = 'default'):
    global presenter_type, provider_type, presenter_obj, provider_obj
    presenter_type = get_presenter(presenter)
    provider_type = get_provider(provider)
    presenter_obj = presenter_type()
    provider_obj = provider_type()
    provider_obj.presenter = presenter_obj
    provider_obj.roomid = roomid


async def running():
    presenter_obj.setup()
    provider_obj.setup()
    await asynchronous_run(provider_obj.run)
    await asynchronous_run(provider_obj.teardown)
    await asynchronous_run(presenter_obj.teardown)


async def gracefully_quit():
    print(f'\nSignal received. Gracefully quitting...')
    await asynchronous_run(provider_obj.teardown)
    await asynchronous_run(presenter_obj.teardown)


def print_version(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__appart__)
    click.echo(f'{__appname__} - Version {__version__}')
    ctx.exit()


def parse_provider(uri: str) -> Tuple[Optional[str], Optional[str]]:
    provider = None
    roomid = None
    parsed = urlparse(uri)
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
    return provider, roomid


@click.command(help=f'{__appname__} - Version {__version__}')
@click.option('--version', '-V', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.argument('roomid', required=True)
@click.option('--provider', '-p', help='Provider name', type=click.Choice(['bilibili', 'douyu', 'huya']))
@click.option('--presenter', help='Presenter name', type=click.Choice(['default']), default='default')
def main(roomid: str, provider: str, presenter: str = 'default'):
    if roomid.startswith('http'):
        provider, roomid = parse_provider(roomid)
    if provider is None:
        click.echo('cannot find provider', err=True)
        sys.exit(1)
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.ensure_future(gracefully_quit()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.ensure_future(gracefully_quit()))
    initialize(roomid, provider, presenter)
    loop.run_until_complete(running())
