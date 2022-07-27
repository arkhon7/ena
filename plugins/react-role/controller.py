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


from ena.cache import set, get, evict


# from aiocache import cached
# from aiocache import Cache
# from aiocache.serializers import PickleSerializer

T = t.TypeVar("T")


async def fetch_all_reaction_role_awares(pool: asyncpg.Pool, guild_id: int) -> t.List[ReactionRoleAware]:

    cache_key = f"{guild_id}:reaction_role_aware:"
    cached = await get(cache_key)

    if cached:
        return cached

    else:
        records = await fetch(pool, "SELECT * FROM react_role_awares WHERE guild_id = $1", guild_id)
        serialized_records: t.List[ReactionRoleAware] = [serialize(ReactionRoleAware, record) for record in records]

        await set(cache_key, serialized_records, ttl=300)
        return serialized_records


async def fetch_reaction_role_aware(pool: asyncpg.Pool, id: str) -> ReactionRoleAware:

    cache_key = f"{id}:reaction_role:"
    cached = await get(cache_key)

    if cached:
        return cached

    else:
        record = await fetchrow(pool, "SELECT * FROM react_role_awares WHERE id = $1", id)

        serialized_record: ReactionRoleAware = serialize(ReactionRoleAware, record)

        await set(cache_key, serialized_record, ttl=60)
        return serialized_record


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

    rr_aware_list_key = f"{guild_id}:reaction_role_aware:"
    await evict(rr_aware_list_key)


async def delete_reaction_role_aware(pool: asyncpg.Pool, id: int, guild_id: int):

    await execute(pool, "DELETE FROM react_role_awares WHERE id = $1", id)

    # evict cache
    rr_aware_key = f"{id}:reaction_role:"
    rr_aware_list_key = f"{guild_id}:reaction_role_aware:"

    await evict(rr_aware_key)
    await evict(rr_aware_list_key)


# reaction role
async def fetch_all_reaction_roles(pool: asyncpg.Pool, guild_id: int) -> t.List[ReactionRole]:

    cache_key = f"{guild_id}:reaction_role:"
    cached = await get(cache_key)

    if cached:
        return cached

    else:
        records = await fetch(pool, "SELECT * FROM react_roles WHERE guild_id = $1", guild_id)
        serialized_records: t.List[ReactionRole] = [serialize(ReactionRole, record) for record in records]

        await set(cache_key, serialized_records, ttl=300)
        return serialized_records


async def fetch_reaction_role(pool: asyncpg.Pool, id: str) -> ReactionRole:

    cache_key = f"{id}:reaction_role:"
    cached = await get(cache_key)

    if cached:
        return cached

    else:
        record = await fetchrow(pool, "SELECT * FROM react_roles WHERE id = $1", id)

        serialized_record: ReactionRole = serialize(ReactionRole, record)

        await set(cache_key, serialized_record, ttl=60)
        return serialized_record


async def insert_reaction_role(
    pool: asyncpg.Pool, role_id: int, emoji_id: int, emoji_name: str, animated: bool, guild_id: int
):
    id = generate_hash(role_id, emoji_id, emoji_name, animated, guild_id)  # primary key id

    await execute(
        pool,
        """
        INSERT INTO react_roles (id, role_id, emoji_id, emoji_name, animated, guild_id)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        id,
        role_id,
        emoji_id,
        emoji_name,
        animated,
        guild_id,
    )

    rr_list_key = f"{guild_id}:reaction_role:"
    await evict(rr_list_key)


async def delete_reaction_role(pool: asyncpg.Pool, id: int, guild_id: int):

    await execute(pool, "DELETE FROM react_roles WHERE id = $1", id)

    # evict cache
    rr_key = f"{id}:reaction_role:"
    rr_list_key = f"{guild_id}:reaction_role:"

    await evict(rr_key)
    await evict(rr_list_key)


# REACTION ROLE PAIRS
# TODO
