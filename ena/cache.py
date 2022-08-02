import logging

import typing as t
import aiocache


T = t.TypeVar("T")


_CACHE = aiocache.Cache()
logging = logging.getLogger(__name__)  # type: ignore


async def set(key: str, value: T, ttl=60) -> None:
    await _CACHE.set(key=key, value=value, ttl=ttl)


async def get(key: str) -> T:
    value: T = await _CACHE.get(key=key)
    return value


async def clear_all():
    await _CACHE.clear()


async def evict(key: str):
    await _CACHE.delete(key)


class CacheOption:
    """
    Cache identifiers for salting the hash, this is to
    ensure correct mapping of data
    """

    EMOJI_ROLE_PAIRS = "EMOJI_ROLE_PAIRS"
    ACTIVE_EMOJI_ROLE_PAIRS = "ACTIVE_EMOJI_ROLE_PAIRS"
