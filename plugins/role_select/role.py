from typing import Optional, List

from sqlalchemy.engine import Engine
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import delete, insert, select


from .models import ReactionRole


async def fetch_all_reaction_role_rows(engine: Engine, guild_id: str) -> Optional[List[Row]]:
    conn: AsyncConnection
    stmt = select(ReactionRole).where(ReactionRole.guild_id == guild_id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)

        rows: Optional[List[Row]] = cursor.fetchall()

        return rows


async def fetch_reaction_role_row(engine: Engine, id: str) -> Optional[Row]:
    conn: AsyncConnection
    stmt = select(ReactionRole).where(ReactionRole.id == id).limit(1)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)

        row: Optional[Row] = cursor.first()

        return row


async def insert_reaction_role_row(
    engine: Engine, id: str, role_id: str, emoji_id: str, emoji_name: str, animated: bool, guild_id: str
):
    conn: AsyncConnection
    stmt = insert(ReactionRole).values(
        id=id, role_id=role_id, emoji_id=emoji_id, emoji_name=emoji_name, animated=animated, guild_id=guild_id
    )

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()


async def update_reaction_role_row(
    engine: Engine,
    old_id: str,
    new_id: str,
    role_id: str,
    emoji_id: str,
    emoji_name: str,
    animated: bool,
    guild_id: str,
):
    conn: AsyncConnection
    stmt = (
        insert(ReactionRole)
        .where(ReactionRole.id == old_id)
        .values(
            id=new_id, role_id=role_id, emoji_id=emoji_id, emoji_name=emoji_name, animated=animated, guild_id=guild_id
        )
    )

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()


async def delete_reaction_role_row(engine: Engine, id: str):
    conn: AsyncConnection
    stmt = delete(ReactionRole).where(ReactionRole.id == id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()
