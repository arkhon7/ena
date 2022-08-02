import asyncpg
import typing as t

from ena.database import fetch, execute, fetchrow
from ena.helpers import create_cache_key

from ena.cache import CacheOption


async def fetch_all_pairs(pool: asyncpg.Pool, guild_id: int) -> t.Optional[t.List[asyncpg.Record]]:

    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE guild_id = $1
    """

    cache_key = create_cache_key(guild_id, CacheOption.EMOJI_ROLE_PAIRS)

    records = await fetch(
        pool,
        query,
        guild_id,
        timeout=5,
        cache_key=cache_key,
    )
    return records


async def fetch_pair(pool: asyncpg.Pool, id: str, guild_id: int) -> t.Optional[asyncpg.Record]:
    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE id = $1
    AND guild_id = $2
    """

    cache_key = create_cache_key(id, guild_id, CacheOption.EMOJI_ROLE_PAIRS)

    record = await fetchrow(
        pool,
        query,
        id,
        guild_id,
        timeout=5,
        cache_key=cache_key,
    )

    return record


async def add_pair(
    pool: asyncpg.Pool,
    id: str,
    role_id: int,
    emoji_id: int,
    emoji_name: str,
    is_animated: bool,
    guild_id: int,
):

    query = """
    INSERT INTO emoji_role_pairs
    VALUES ($1, $2, $3, $4, $5, $6)
    """

    cached_from_id_key = create_cache_key(id, guild_id, CacheOption.EMOJI_ROLE_PAIRS)
    cached_from_guild_id_key = create_cache_key(guild_id, CacheOption.EMOJI_ROLE_PAIRS)

    await execute(
        pool,
        query,
        id,
        role_id,
        emoji_id,
        emoji_name,
        is_animated,
        guild_id,
        timeout=5,
        evict_keys=[
            cached_from_id_key,
            cached_from_guild_id_key,
        ],
    )


async def delete_pair(pool: asyncpg.Pool, id: str, guild_id: int):
    query = """
    DELETE FROM emoji_role_pairs
    WHERE id = $1
    AND guild_id = $2
    """

    cached_from_id_key = create_cache_key(id, guild_id, CacheOption.EMOJI_ROLE_PAIRS)
    cached_from_guild_id_key = create_cache_key(guild_id, CacheOption.EMOJI_ROLE_PAIRS)

    await execute(
        pool,
        query,
        id,
        guild_id,
        timeout=5,
        evict_keys=[
            cached_from_id_key,
            cached_from_guild_id_key,
        ],
    )


# active emoji role pairs table
async def fetch_all_active_pairs_by_message(pool: asyncpg.Pool, message_id: int, guild_id: int):

    query = """
    SELECT
        erp.id,
        erp.role_id,
        erp.emoji_id,
        erp.emoji_name,
        erp.is_animated,
        aerp.message_id,
        aerp.channel_id,
        aerp.guild_id
    FROM active_emoji_role_pairs AS aerp
    JOIN emoji_role_pairs AS erp
        ON erp.id = aerp.pair_id
    WHERE aerp.message_id = $1
    AND aerp.guild_id = $2
    """
    cache_key = create_cache_key(message_id, guild_id, CacheOption.ACTIVE_EMOJI_ROLE_PAIRS)
    records = await fetch(
        pool,
        query,
        message_id,
        guild_id,
        cache_key=cache_key,
    )

    return records


async def add_active_pair(
    pool: asyncpg.Pool,
    id: str,
    pair_id: str,
    message_id: int,
    channel_id: int,
    guild_id: int,
):

    query = """
    INSERT INTO active_emoji_role_pairs
    (id, pair_id, message_id, channel_id, guild_id)
    VALUES ($1, $2, $3, $4, $5)
    """

    cached_from_msg_id_key = create_cache_key(message_id, guild_id, CacheOption.ACTIVE_EMOJI_ROLE_PAIRS)

    await execute(
        pool,
        query,
        id,
        pair_id,
        message_id,
        channel_id,
        guild_id,
        evict_keys=[cached_from_msg_id_key],
    )


async def delete_active_pair(
    pool: asyncpg.Pool,
    id: str,
    message_id: int,
    channel_id: int,
    guild_id: int,
):
    query = """
    DELETE FROM active_emoji_role_pairs
    WHERE id = $1
    AND message_id = $2
    AND channel_id = $3
    AND guild_id = $4
    """

    cached_from_msg_id_key = create_cache_key(message_id, guild_id, CacheOption.ACTIVE_EMOJI_ROLE_PAIRS)

    await execute(
        pool,
        query,
        id,
        message_id,
        channel_id,
        guild_id,
        timeout=5,
        evict_keys=[cached_from_msg_id_key],
    )


async def delete_all_active_pairs_by_message(
    pool: asyncpg.Pool,
    message_id: int,
    channel_id: int,
    guild_id: int,
):
    query = """
    DELETE FROM active_emoji_role_pairs
    WHERE message_id = $1
    AND channel_id = $2
    AND guild_id = $3
    """

    cached_from_msg_id_key = create_cache_key(message_id, guild_id, CacheOption.ACTIVE_EMOJI_ROLE_PAIRS)

    await execute(
        pool,
        query,
        message_id,
        channel_id,
        guild_id,
        timeout=5,
        evict_keys=[cached_from_msg_id_key],
    )
