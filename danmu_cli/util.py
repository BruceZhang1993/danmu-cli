import asyncio
from functools import partial
from typing import Awaitable


def asynchronous_run(callable_, *args, **kwargs) -> Awaitable:
    if asyncio.iscoroutinefunction(callable_):
        return callable_(*args, **kwargs)
    else:
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, partial(callable_, *args, **kwargs))
