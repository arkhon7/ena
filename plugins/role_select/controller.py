from __future__ import annotations

from typing import Optional, List

from dataclasses import dataclass


from sqlalchemy.engine import Engine
from sqlalchemy.engine.row import Row


from .helpers import generate_hash
from .helpers import serialize

from .aware import fetch_all_reaction_role_aware_rows
from .aware import fetch_reaction_role_aware_row
from .aware import insert_reaction_role_aware_row
from .aware import delete_reaction_role_aware_row

from .role import fetch_all_reaction_role_rows
from .role import fetch_reaction_role_row
from .role import insert_reaction_role_row
from .role import delete_reaction_role_row

from .pair import fetch_all_reaction_role_pair_rows
from .pair import fetch_reaction_role_pair_row
from .pair import insert_reaction_role_pair_row
from .pair import delete_reaction_role_pair_row

from ena.cache import evict
from ena.cache import set
from ena.cache import get
from ena.cache import generate_cache_key


# structs
@dataclass
class ReactionRoleAwareData:
    id: str
    message_id: str
    channel_id: str
    guild_id: str


@dataclass
class ReactionRoleData:
    id: str
    role_id: str
    emoji_id: str
    emoji_name: str
    animated: bool
    guild_id: str


# REACTION ROLE AWARE MESSAGE CONTROLLERS


async def fetch_all_reaction_role_awares(engine: Engine, guild_id: str) -> Optional[List[ReactionRoleAwareData]]:

    cache_key = generate_cache_key(f"{guild_id}:rr_aware")
    cached: List[ReactionRoleAwareData] = await get(cache_key)

    if cached:
        return cached

    else:
        rows: Optional[List[Row]] = await fetch_all_reaction_role_aware_rows(engine, guild_id)
        if rows:
            serialized_rows = [
                serialize(ReactionRoleAwareData, id=row[0], message_id=row[1], channel_id=row[2], guild_id=row[3])
                for row in rows
            ]

            await set(cache_key, value=serialized_rows, ttl=300)

            return serialized_rows

        return None


async def fetch_reaction_role_aware(engine: Engine, id: str, guild_id: str) -> Optional[ReactionRoleAwareData]:

    cache_key = generate_cache_key(f"{guild_id}:rr_aware")
    cached: List[ReactionRoleAwareData] = await get(cache_key)

    """this is somewhat awkward, shud I iterate on cache to get the value? or shud I just cache this separately?
    currently iterating to the cache btw."""

    if cached:
        for aware in cached:
            if aware.id == id:
                return aware

        else:
            row = await fetch_reaction_role_aware_row(engine, id)

            if row:
                return serialize(
                    ReactionRoleAwareData, id=row[0], message_id=row[1], channel_id=row[2], guild_id=row[3]
                )

    return None


async def insert_react_role_aware(engine: Engine, message_id: str, channel_id: str, guild_id: str):
    cache_key = generate_cache_key(f"{guild_id}:rr_aware")
    cached: List[ReactionRoleAwareData] = await get(cache_key)

    id = generate_hash(guild_id, channel_id, message_id)
    await insert_reaction_role_aware_row(engine, id, message_id, channel_id, guild_id)

    if cached:
        await evict(cache_key)


async def delete_react_role_aware(engine: Engine, id: str, guild_id: str):
    cache_key = generate_cache_key(f"{guild_id}:rr_aware")
    cached: List[ReactionRoleAwareData] = await get(cache_key)

    await delete_reaction_role_aware_row(engine, id)

    if cached:
        await evict(cache_key)


# async def update_react_role_aware(engine: Engine, id, message_id: str, channel_id: str, guild_id: str):

#     new_id = generate_hash(guild_id, channel_id, message_id)
#     await update_reaction_role_aware_row(engine, id, new_id, message_id, channel_id, guild_id)


async def fetch_all_reaction_roles(engine: Engine, guild_id: str) -> Optional[List[ReactionRoleData]]:
    cache_key = generate_cache_key(f"{guild_id}:rr")
    cached: List[ReactionRoleData] = await get(cache_key)

    if cached:
        return cached

    else:
        rows: Optional[List[Row]] = await fetch_all_reaction_role_rows(engine, guild_id)
        if rows:
            serialized_rows = [
                serialize(
                    ReactionRoleData,
                    id=row[0],
                    role_id=row[1],
                    emoji_id=row[2],
                    emoji_name=row[3],
                    animated=row[4],
                    guild_id=row[5],
                )
                for row in rows
            ]

            await set(cache_key, value=serialized_rows, ttl=60)

            return serialized_rows

        return None


async def fetch_reaction_role(engine: Engine, id: str, guild_id: str) -> Optional[ReactionRoleData]:
    cache_key = generate_cache_key(f"{guild_id}:rr")
    cached: List[ReactionRoleData] = await get(cache_key)

    """again, this caching implementation seems awkward too"""

    if cached:
        for aware in cached:
            if aware.id == id:
                return aware

        else:
            row = await fetch_reaction_role_row(engine, id)

            if row:
                return serialize(
                    ReactionRoleData,
                    id=row[0],
                    role_id=row[1],
                    emoji_id=row[2],
                    emoji_name=row[3],
                    animated=row[4],
                    guild_id=row[5],
                )

    return None


async def insert_react_role(
    engine: Engine, role_id: str, emoji_id: str, emoji_name: str, animated: bool, guild_id: str
):
    cache_key = generate_cache_key(f"{guild_id}:rr")
    cached: List[ReactionRoleData] = await get(cache_key)

    id = generate_hash(role_id, emoji_id, emoji_name, str(animated), guild_id)
    await insert_reaction_role_row(engine, id, role_id, emoji_id, emoji_name, animated, guild_id)

    if cached:
        evict(cache_key)


async def delete_react_role(engine: Engine, id: str, guild_id: str):
    cache_key = generate_cache_key(f"{guild_id}:rr")
    cached: List[ReactionRoleData] = await get(cache_key)

    await delete_reaction_role_row(engine, id)

    if cached:
        evict(cache_key)


async def fetch_all_reaction_role_pairs(engine: Engine, guild_id: str):

    rows: Optional[List[Row]] = await fetch_all_reaction_role_pair_rows(engine, guild_id)
    if rows:
        return rows  # serialize this

    return None


async def fetch_reaction_role_pair(engine: Engine, id: str, guild_id: str):
    row = await fetch_reaction_role_pair_row(engine, id)
    if row:
        return row  # serialize this

    return None


async def insert_reaction_role_pair(engine: Engine, rr_id: str, rr_aware_id: str, guild_id: str):
    id = generate_hash(rr_id, rr_aware_id, guild_id)
    await insert_reaction_role_pair_row(engine, id, rr_id, rr_aware_id, guild_id)


async def delete_reaction_role_pair(engine: Engine, id: str, guild_id: str):
    await delete_reaction_role_pair_row(engine, id)
