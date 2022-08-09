import asyncpg
import logging
import typing as t

from contextlib import asynccontextmanager


logging = logging.getLogger(__name__)  # type:ignore


class EnaDatabase:
    def __init__(self, dsn: str, schema: t.Optional[str] = None) -> None:
        self._pool: t.Optional[asyncpg.Pool] = None
        self._schema: t.Optional[str] = schema
        self._dsn: str = dsn

    # event methods
    async def insert_default_guild_ids(self, guilds: t.Sequence[int]):
        for guild_id in guilds:
            await self.execute("INSERT INTO guilds VALUES ($1) ON CONFLICT DO NOTHING", guild_id)
            logging.info("initialized default guild id '{}'".format(guild_id))

    @asynccontextmanager
    async def acquire(self) -> t.AsyncIterator[asyncpg.Connection]:

        if not self._pool:

            raise Exception("database not connected")

        async with self._pool.acquire() as conn:
            yield conn

    async def connect(self):

        self._pool = await asyncpg.create_pool(self._dsn)

        logging.info(f"created pool connection '{self._pool}'")

    async def create_schema(self):

        if self._schema:
            async with self.acquire() as conn:
                try:
                    with open(self._schema, "r") as schema:
                        await conn.execute(schema.read())
                        logging.info("done creating schema from the given path '{}'".format(self._schema))

                except FileNotFoundError:
                    logging.warn(
                        "failed schema creation, schema is not found from the given path '{}'".format(self._schema)
                    )

        else:
            logging.info("no schema specified, skipping schema creation")

    # database queries
    async def fetch(
        self,
        query: str,
        *args,
        timeout: t.Optional[float] = None,
        record_class: t.Optional[asyncpg.Record] = None,
    ):

        async with self.acquire() as conn:
            records = await conn.fetch(
                query,
                *args,
                timeout=timeout,
                record_class=record_class,
            )

            return records

    async def fetchrow(
        self,
        query: str,
        *args,
        timeout: t.Optional[float] = None,
        record_class: t.Optional[asyncpg.Record] = None,
    ):

        async with self.acquire() as conn:
            record = await conn.fetchrow(
                query,
                *args,
                timeout=timeout,
                record_class=record_class,
            )

            return record

    async def execute(self, query: str, *args, timeout=None):

        async with self.acquire() as conn:
            await conn.execute(
                query,
                *args,
                timeout=timeout,
            )
