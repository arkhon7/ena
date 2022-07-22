from typing import Optional, List

from sqlalchemy.engine import Engine
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import delete, insert, select

from .models import ReactionRole, ReactionRoleAware, ReactionRolePair


async def fetch_all_reaction_role_pair_rows(engine: Engine, guild_id: str) -> Optional[List[Row]]:

    conn: AsyncConnection
    stmt = select(ReactionRolePair).where(ReactionRolePair.guild_id == guild_id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)

        rows: Optional[List[Row]] = cursor.fetchall()

        return rows


async def fetch_reaction_role_pair_row(engine: Engine, id: str) -> Optional[Row]:
    conn: AsyncConnection
    # stmt = select(ReactionRolePair).where(ReactionRolePair.id == id).limit(1)
    stmt = (
        select(ReactionRolePair)
        .join(ReactionRole, ReactionRole.id == ReactionRolePair.rr_id)
        .join(ReactionRoleAware, ReactionRoleAware.id == ReactionRolePair.rra_id)
    )

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)

        row: Optional[Row] = cursor.first()

        return row


async def insert_reaction_role_pair_row(engine: Engine, id: str, rr_id: str, rr_aware_id: str, guild_id: str):
    conn: AsyncConnection
    stmt = insert(ReactionRolePair).values(id=id, rr_id=rr_id, rr_aware_id=rr_aware_id, guild_id=guild_id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()


async def update_reaction_role_pair_row(
    engine: Engine, old_id: str, new_id: str, rr_id: str, rr_aware_id: str, guild_id: str
):
    conn: AsyncConnection
    stmt = (
        insert(ReactionRolePair)
        .where(ReactionRolePair.id == old_id)
        .values(id=new_id, rr_id=rr_id, rr_aware_id=rr_aware_id, guild_id=guild_id)
    )

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()


async def delete_reaction_role_pair_row(engine: Engine, id: str):
    conn: AsyncConnection
    stmt = delete(ReactionRolePair).where(ReactionRolePair.id == id)

    async with engine.connect() as conn:
        cursor: CursorResult = await conn.execute(stmt)
        cursor.close()
        await conn.commit()
