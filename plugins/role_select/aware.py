from typing import Optional, List

from sqlalchemy.engine import Engine
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import delete, insert, select


from .models import ReactionRoleAware


async def fetch_all_reaction_role_aware_rows(engine: Engine, guild_id: str) -> Optional[List[Row]]:
    conn: AsyncConnection
    stmt = select(ReactionRoleAware).where(ReactionRoleAware.guild_id == guild_id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)

        rows: Optional[List[Row]] = cursor.fetchall()

        return rows


async def fetch_reaction_role_aware_row(engine: Engine, id: str) -> Optional[Row]:
    conn: AsyncConnection
    stmt = select(ReactionRoleAware).where(ReactionRoleAware.id == id).limit(1)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)

        row: Optional[Row] = cursor.first()

        return row


async def insert_reaction_role_aware_row(engine: Engine, id: str, message_id: str, channel_id: str, guild_id: str):
    conn: AsyncConnection
    stmt = insert(ReactionRoleAware).values(id=id, message_id=message_id, channel_id=channel_id, guild_id=guild_id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()


async def update_reaction_role_aware_row(
    engine: Engine, old_id: str, new_id: str, message_id: str, channel_id: str, guild_id: str
):
    conn: AsyncConnection
    stmt = (
        insert(ReactionRoleAware)
        .where(ReactionRoleAware.id == old_id)
        .values(id=new_id, message_id=message_id, channel_id=channel_id, guild_id=guild_id)
    )

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()


async def delete_reaction_role_aware_row(engine: Engine, id: str):
    conn: AsyncConnection
    stmt = delete(ReactionRoleAware).where(ReactionRoleAware.id == id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()
