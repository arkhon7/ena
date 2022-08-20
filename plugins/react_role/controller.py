import asyncpg
import typing as t
import logging

from ena.database import EnaDatabase
from ena.cache import EnaCache


logging = logging.getLogger(__name__)  # type:ignore


async def fetch_all_pairs(database: EnaDatabase, cache: EnaCache, guild_id: int) -> t.Optional[t.List[asyncpg.Record]]:

    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE guild_id = $1
    """

    fetch = cache.cached([(guild_id, "emoji_role_pairs"), "list"], database.fetch, ttl=300)
    records = await fetch(query, guild_id, timeout=5)

    return records


async def fetch_pair(database: EnaDatabase, cache: EnaCache, id: str, guild_id: int) -> t.Optional[asyncpg.Record]:
    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE id = $1
    AND guild_id = $2
    """

    #
    fetchrow = cache.cached([(guild_id, "emoji_role_pairs"), "ids", id], database.fetchrow, ttl=300)
    record = await fetchrow(query, id, guild_id, timeout=5)

    return record
    #


async def add_pair(
    database: EnaDatabase,
    cache: EnaCache,
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

    await database.execute(
        query,
        id,
        role_id,
        emoji_id,
        emoji_name,
        is_animated,
        guild_id,
        timeout=5,
    )

    # refresh cache
    await cache.delete((guild_id, "emoji_role_pairs"))
    await cache.delete((guild_id, "active_emoji_role_pairs"))


async def delete_pair(database: EnaDatabase, cache: EnaCache, id: str, guild_id: int):
    query = """
    DELETE FROM emoji_role_pairs
    WHERE id = $1
    AND guild_id = $2
    """

    await database.execute(
        query,
        id,
        guild_id,
        timeout=5,
    )

    # refresh cache
    await cache.delete((guild_id, "emoji_role_pairs"))
    await cache.delete((guild_id, "active_emoji_role_pairs"))


# active emoji role pairs table
async def fetch_all_active_pairs_by_message(database: EnaDatabase, cache: EnaCache, message_id: int, guild_id: int):

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

    #
    fetch = cache.cached(
        [(guild_id, "active_emoji_role_pairs"), message_id],
        database.fetch,
        ttl=300,
    )

    records = await fetch(query, message_id, guild_id, timeout=5)
    return records
    #


async def add_active_pair(
    database: EnaDatabase,
    cache: EnaCache,
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

    await database.execute(
        query,
        id,
        pair_id,
        message_id,
        channel_id,
        guild_id,
    )

    await cache.delete((guild_id, "active_emoji_role_pairs"))


async def delete_active_pair(
    database: EnaDatabase,
    cache: EnaCache,
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

    await database.execute(
        query,
        id,
        message_id,
        channel_id,
        guild_id,
        timeout=5,
    )
    await cache.delete((guild_id, "active_emoji_role_pairs"))


async def delete_all_active_pairs_by_message(
    database: EnaDatabase,
    cache: EnaCache,
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

    await database.execute(
        query,
        message_id,
        channel_id,
        guild_id,
        timeout=5,
    )

    await cache.delete((guild_id, "active_emoji_role_pairs"))
