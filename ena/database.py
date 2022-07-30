import asyncpg

import logging
import lightbulb as lb
import typing as t

from ena.cache import set, get, evict


logging = logging.getLogger(__name__)  # type:ignore


async def _load_database(bot: lb.BotApp, dsn: str = None, schema_path: str = None):

    pool: asyncpg.Pool = await asyncpg.create_pool(dsn=dsn)

    await initialize_schema(pool, schema_path)

    bot.d.POOL = pool

    logging.info("pool name is set into 'POOL'")


async def initialize_schema(pool: asyncpg.Pool, schema_path: str = None):
    conn: asyncpg.Connection

    if schema_path:
        logging.info(f"given schema path '{schema_path}'.")

        async with pool.acquire() as conn:
            try:
                with open(schema_path, "r") as schema:
                    await conn.execute(schema.read())
                    logging.info(f"done creating schema from '{schema_path}' with '{conn}'.")

            except FileNotFoundError:
                logging.warn(f"failed schema execution, schema is not found from '{schema_path}'.")

    else:
        logging.info("no schema path given, so no schema created.")


# functions
async def fetch(pool: asyncpg.Pool, query: str, *args, cache_key: str, timeout=None) -> t.List[asyncpg.Record]:
    conn: asyncpg.Connection

    async with pool.acquire() as conn:

        cached: t.List[asyncpg.Record] = await get(cache_key)
        if cached:
            return cached

        else:
            records = await conn.fetch(query, *args, timeout=timeout)

            await set(cache_key, records)
            return records


async def fetchrow(pool: asyncpg.Pool, query: str, *args, cache_key: str, timeout=None) -> asyncpg.Record:
    conn: asyncpg.Connection

    async with pool.acquire() as conn:

        cached: t.List[asyncpg.Record] = await get(cache_key)
        if cached:
            return cached

        else:
            record = await conn.fetchrow(query, *args, timeout=timeout)

            await set(cache_key, record)
            return record


async def execute(pool: asyncpg.Pool, query: str, *args, timeout=None, evict_keys: t.List[str] = None) -> None:
    conn: asyncpg.Connection

    async with pool.acquire() as conn:
        await conn.execute(query, *args, timeout=timeout)

        if evict_keys:

            for key in evict_keys:
                await evict(key)
