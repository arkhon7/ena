import asyncpg
import typing as t

from ena.database import fetch, execute, fetchrow
from ena.helpers import create_hash
from ena.cache import CacheOption


async def fetch_all_pairs_by_guild(pool: asyncpg.Pool, guild_id: int) -> t.Optional[t.List[asyncpg.Record]]:

    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE guild_id = $1
    """

    records = await fetch(
        pool,
        query,
        guild_id,
        timeout=5,
        cache_key=create_hash(
            guild_id,
            CacheOption.EMOJI_ROLE_PAIRS,
        ),
    )
    return records


async def fetch_pair(pool: asyncpg.Pool, id: str, guild_id: int) -> t.Optional[asyncpg.Record]:
    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE id = $1
    AND guild_id = $2
    """

    record = await fetchrow(
        pool,
        query,
        id,
        guild_id,
        timeout=5,
        cache_key=create_hash(
            id,
            guild_id,
            CacheOption.EMOJI_ROLE_PAIRS,
        ),
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
            create_hash(
                guild_id,
                CacheOption.EMOJI_ROLE_PAIRS,
            ),
            create_hash(
                id,
                guild_id,
                CacheOption.EMOJI_ROLE_PAIRS,
            ),
        ],
    )


async def delete_pair(pool: asyncpg.Pool, id: str, guild_id: int):
    query = """
    DELETE FROM emoji_role_pairs WHERE id = $1 AND guild_id = $2
    """

    await execute(
        pool,
        query,
        id,
        guild_id,
        timeout=5,
        evict_keys=[
            create_hash(
                guild_id,
                CacheOption.EMOJI_ROLE_PAIRS,
            ),
            create_hash(
                id,
                guild_id,
                CacheOption.EMOJI_ROLE_PAIRS,
            ),
        ],
    )


# active emoji role pairs table methods
async def fetch_all_active_pairs(pool: asyncpg.Pool, guild_id: int):
    # TODO TEST THIS SHIT
    # and you should query all of its relationships

    query = """
    SELECT
        erp.id,
        erp.role_id,
        erp.emoji_id,
        erp.emoji_name,
        message_id,
        channel_id,
        aerp.guild_id
    FROM active_emoji_role_pairs AS aerp
    JOIN emoji_role_pairs AS erp
        ON erp.id = aerp.pair_id
    WHERE guild_id = $1
    """

    records = await fetch(
        pool,
        query,
        guild_id,
        cache_key=create_hash(
            guild_id,
            CacheOption.ACTIVE_EMOJI_ROLE_PAIRS,
        ),
    )

    return records


async def fetch_active_pair(pool: asyncpg.Pool, pair_id: str, guild_id: int):
    ...


async def add_active_pair():
    ...


async def delete_active_pair():
    ...
