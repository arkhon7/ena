import logging

# import asyncio
import typing
import hashlib

import enum

import aiocache


K = typing.TypeVar("K")
V = typing.TypeVar("V")


_CACHE = aiocache.Cache()
logging = logging.Logger(__name__)  # type: ignore


class Cache(enum.Enum):
    """An Enum of cache identifiers"""

    # reaction roles
    REACTION_ROLE_AWARE = "reaction-role-aware-cache"
    REACTION_ROLE = "reaction-role-cache"


async def set(key: K, value: V, ttl=60) -> None:
    await _CACHE.set(key=key, value=value, ttl=ttl)
    logging.debug(f"CACHE_SET: (key:{key}, value:{value})")


async def get(key: K) -> V:
    value: V = await _CACHE.get(key=key)
    logging.debug(f"CACHE_GET: (value:{value})")

    return value


def generate_cache_hash(identifier: typing.Any, key: Cache) -> str:
    hashing_string: str = str(identifier) + key.value
    cache_key: str = hashlib.sha256(hashing_string.encode()).hexdigest()

    return cache_key


async def set_guild_cache(guild_id: str, key: Cache, value: V) -> None:
    cache_key: str = generate_cache_hash(identifier=guild_id, key=key)

    await set(key=cache_key, value=value, ttl=300)


async def get_guild_cache(guild_id: str, key: Cache) -> V:
    cache_key: str = generate_cache_hash(identifier=guild_id, key=key)

    value: V = await get(key=cache_key)
    return value
