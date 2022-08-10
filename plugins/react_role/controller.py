import asyncpg
import typing as t
import logging

from ena.database import EnaDatabase
from ena.cache import EnaCache


logging = logging.getLogger(__name__)  # type:ignore


# cache shapes
class EmojiRolePairCache(t.TypedDict):
    ids: t.Dict[str, asyncpg.Record]
    by_message: t.Dict[int, t.List[asyncpg.Record]]
    by_guild: t.List[asyncpg.Record]


class ActiveEmojiRolePairCache(t.TypedDict):
    by_message: t.Dict[int, t.List[asyncpg.Record]]


async def fetch_all_pairs(database: EnaDatabase, cache: EnaCache, guild_id: int) -> t.Optional[t.List[asyncpg.Record]]:

    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE guild_id = $1
    """

    key = "{}:erp".format(guild_id)
    cached_slice: EmojiRolePairCache = await cache.get(key)

    if cached_slice:
        cached: t.List[asyncpg.Record] = cached_slice["by_guild"]

        if len(cached) != 0:
            return cached

        else:
            # cache if slice found but role pairs by guild is empty
            records = await database.fetch(query, guild_id, timeout=5)
            cached_slice["by_guild"] = records

            await cache.set(key, value=cached_slice)
            #

            return records

    else:
        records = await database.fetch(query, guild_id, timeout=5)

        # cache if no slice found
        slice: EmojiRolePairCache = {"ids": {}, "by_guild": records}
        await cache.set(key, value=slice)
        #

        return records


async def fetch_pair(database: EnaDatabase, cache: EnaCache, id: str, guild_id: int) -> t.Optional[asyncpg.Record]:
    query = """
    SELECT *
    FROM emoji_role_pairs
    WHERE id = $1
    AND guild_id = $2
    """
    key = "{}:erp".format(guild_id)
    cached_slice: EmojiRolePairCache = await cache.get(key)

    if cached_slice:
        cached_ids: t.Dict[str, t.Any] = cached_slice["ids"]

        if cached := cached_ids.get(id):
            return cached

        else:
            record = await database.fetchrow(query, id, guild_id, timeout=5)
            cached_slice["ids"][id] = record

            await cache.set(key, value=cached_slice)

            return record

    else:
        record = await database.fetchrow(query, id, guild_id, timeout=5)
        slice: EmojiRolePairCache = {"ids": {id: record}, "by_guild": []}
        await cache.set(key, value=slice)
        return record


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
    key = "{}:erp".format(guild_id)
    await cache.delete(key)

    key = "{}:aerp".format(guild_id)
    await cache.delete(key)


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
    key = "{}:erp".format(guild_id)
    await cache.delete(key)

    key = "{}:aerp".format(guild_id)
    await cache.delete(key)


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

    key = "{}:aerp".format(guild_id)
    cached_slice: ActiveEmojiRolePairCache = await cache.get(key)

    if cached_slice:
        cached_aerp_by_msg: t.Dict[int, t.List] = cached_slice["by_message"]

        if cached := cached_aerp_by_msg.get(message_id):
            if cached:
                return cached
        else:
            records = await database.fetch(
                query,
                message_id,
                guild_id,
            )

            cached_slice["by_message"][message_id] = records

            await cache.set(key, value=cached_slice)

            return records

    else:

        records = await database.fetch(
            query,
            message_id,
            guild_id,
        )

        slice: ActiveEmojiRolePairCache = {"by_message": {message_id: records}}
        await cache.set(key, value=slice)

        return records


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

    key = "{}:aerp".format(guild_id)
    await cache.delete(key)


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
    key = "{}:aerp".format(guild_id)
    await cache.delete(key)


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

    key = "{}:aerp".format(guild_id)
    await cache.delete(key)


# TODO implement a cache struct
