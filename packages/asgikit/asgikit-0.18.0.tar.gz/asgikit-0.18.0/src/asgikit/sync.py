from functools import partial

from anyio import to_thread

__all__ = ("run_sync",)


async def run_sync(target, *args, **kwargs):
    return await to_thread.run_sync(partial(target, *args, **kwargs))
