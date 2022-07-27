from __future__ import annotations

import asyncpg
import typing as t

from .helpers import generate_hash

from .models import ReactionRoleAware
from .models import ReactionRolePair
from .models import ReactionRole
from .models import serialize

from ena.database import fetch
from ena.database import fetchrow
from ena.database import execute

from aiocache import cached
from aiocache import Cache
from aiocache.serializers import PickleSerializer

T = t.TypeVar("T")


def create_key(func: t.Callable, *args, **kwargs):

    args_k = "".join([str(arg) for arg in args if not isinstance(arg, asyncpg.Pool)])
    kwargs_k = "".join([str(kwarg) for kwarg in kwargs if not isinstance(kwarg, asyncpg.Pool)])

    return func.__name__ + args_k + kwargs_k


@cached(ttl=30, serializer=PickleSerializer(), key_builder=create_key)
async def fetch_all_reaction_role_awares(pool: asyncpg.Pool, guild_id: int) -> t.List[ReactionRoleAware]:

    records = await fetch(pool, "SELECT * FROM react_role_awares WHERE guild_id = $1", guild_id)

    serialized: t.List[ReactionRoleAware] = [serialize(ReactionRoleAware, record) for record in records]

    return serialized


@cached(ttl=30, serializer=PickleSerializer(), key_builder=create_key)
async def fetch_reaction_role_aware(pool: asyncpg.Pool, id: int) -> ReactionRoleAware:

    record = await fetchrow(pool, "SELECT * FROM react_role_awares WHERE id = $1", id)

    serialized: ReactionRoleAware = serialize(ReactionRoleAware, record)

    return serialized


async def insert_reaction_role_aware(pool: asyncpg.Pool, message_id: int, channel_id: int, guild_id: int):

    id = generate_hash(message_id, channel_id, guild_id)  # primary key id

    await execute(
        pool,
        """
        INSERT INTO react_role_awares (id, message_id, channel_id, guild_id)
        VALUES ($1, $2, $3, $4)
        """,
        id,
        message_id,
        channel_id,
        guild_id,
    )


async def delete_reaction_role_aware(pool: asyncpg.Pool, id: int, guild_id: int):

    await execute(pool, "DELETE FROM react_role_awares WHERE id = $1", id)

    # delete cache
    cached_awares: Cache.MEMORY = fetch_all_reaction_role_awares.cache
    cached_aware: Cache.MEMORY = fetch_reaction_role_aware.cache

    cached_key_by_id = create_key(fetch_reaction_role_aware, id)
    cached_key_by_guild_id = create_key(fetch_all_reaction_role_awares, guild_id)

    await cached_aware.delete(cached_key_by_id)  # delete the cached id
    await cached_awares.delete(cached_key_by_guild_id)  # delete the cached list by id
