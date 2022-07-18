from __future__ import annotations

import typing


from sqlalchemy.engine import Engine
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy import delete, insert, select

from .models import ReactionRoleAware
from .models import ReactionRole
from .helpers import serialize


ModelType = typing.Union[ReactionRole, ReactionRoleAware]


# structs
class ReactionRoleAwareData:
    def __init__(self, id: str, message_id: str, channel_id: str, guild_id: str) -> None:
        self.id = id
        self.message_id = message_id
        self.channel_id = channel_id
        self.guild_id = guild_id


class ReactionRoleData:
    def __init__(self, id: str, role_id: str, emoji_id: str, emoji_name: str, guild_id: str) -> None:
        self.id = id
        self.role_id = role_id
        self.emoji_id = emoji_id
        self.emoji_name = emoji_name
        self.guild_id = guild_id


# REACTION ROLE AWARE MESSAGE CONTROLLERS


async def fetch_reaction_role_aware(engine: Engine, rra_id: str) -> typing.Optional[ReactionRoleAwareData]:

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(
            select(ReactionRoleAware).where(ReactionRoleAware.id == rra_id).limit(1)
        )
        row: typing.Optional[Row] = cursor.first()

        if row:
            result: typing.Optional[ReactionRoleAwareData] = serialize(
                ReactionRoleAwareData, id=row[0], message_id=row[1], channel_id=row[2], guild_id=row[3]
            )

            cursor.close()
            return result

        else:
            cursor.close()
            return None


async def fetch_all_reaction_role_aware(
    engine: Engine, guild_id: str
) -> typing.Optional[typing.List[ReactionRoleAwareData]]:

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(
            select(ReactionRoleAware).where(ReactionRoleAware.guild_id == guild_id)
        )
        rows: typing.Optional[Row] = cursor.fetchall()

        if rows:
            result: typing.List[ReactionRoleAwareData] = [
                serialize(ReactionRoleAwareData, id=row[0], message_id=row[1], channel_id=row[2], guild_id=row[3])
                for row in rows
            ]

            cursor.close()
            return result

        else:
            cursor.close()
            return None


async def add_reaction_role_aware(
    engine: Engine,
    rra_id: str,
    channel_id: str,
    message_id: str,
    guild_id: str,
):

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(
            insert(ReactionRoleAware).values(id=rra_id, message_id=message_id, channel_id=channel_id, guild_id=guild_id)
        )
        cursor.close()
        await conn.commit()


async def delete_reaction_role_aware(engine: Engine, rra_id: str):

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(delete(ReactionRoleAware).where(ReactionRoleAware.id == rra_id))
        cursor.close()
        await conn.commit()


# REACTION ROLE CONTROLLERS


async def fetch_all_reaction_role(engine: Engine, guild_id: str) -> typing.Optional[typing.List[ReactionRoleData]]:
    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(select(ReactionRole).where(ReactionRole.guild_id == guild_id))
        rows: typing.Optional[Row] = cursor.fetchall()

        if rows:

            result: typing.Optional[typing.List[ReactionRoleData]] = [
                serialize(
                    ReactionRoleData, id=row[0], role_id=row[1], emoji_id=row[2], emoji_name=row[3], guild_id=row[4]
                )
                for row in rows
            ]
            cursor.close()
            return result

        else:
            cursor.close()
            return None


async def fetch_reaction_role(engine: Engine, rr_id: str) -> typing.Optional[ReactionRoleData]:

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(select(ReactionRole).where(ReactionRole.id == rr_id))
        row: typing.Optional[Row] = cursor.first()

        if row:
            result: typing.Optional[ReactionRoleData] = serialize(
                ReactionRoleData, id=row[0], role_id=row[1], emoji_id=row[2], emoji_name=row[3], guild_id=row[4]
            )

            cursor.close()
            return result

        else:
            cursor.close()
            return None


async def add_reaction_role(engine: Engine, rr_id: str, role_id: str, emoji_id: str, emoji_name: str, guild_id: str):

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(
            insert(ReactionRole).values(
                id=rr_id, role_id=role_id, emoji_id=emoji_id, emoji_name=emoji_name, guild_id=guild_id
            )
        )
        cursor.close()

        await conn.commit()


async def delete_reaction_role(engine: Engine, rr_id: str):

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(delete(ReactionRole).where(ReactionRole.id == rr_id))
        cursor.close()
        await conn.commit()
