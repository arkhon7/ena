import logging

import typing
import hashlib


import aiocache


T = typing.TypeVar("T")


_CACHE = aiocache.Cache()
logging = logging.getLogger(__name__)  # type: ignore


async def set(key: str, value: T, ttl=60) -> None:
    await _CACHE.set(key=key, value=value, ttl=ttl)
    logging.debug(f"CACHE_SET: (key:{key}, value:{value})")


async def get(key: str) -> T:
    value: T = await _CACHE.get(key=key)
    logging.debug(f"CACHE_GET: (value:{value})")

    return value


async def evict(key: str):
    await _CACHE.delete(key)
    logging.debug(f"CACHE_EVICT: (key:{key})")


def generate_cache_key(identifier: str) -> str:
    hashing_string: str = identifier
    cache_key: str = hashlib.sha1(hashing_string.encode()).hexdigest()

    return cache_key
