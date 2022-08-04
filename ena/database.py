import asyncpg

import logging

import typing as t
import hikari as hk
import lightbulb as lb

from contextlib import asynccontextmanager


logging = logging.getLogger(__name__)  # type:ignore


class EnaDatabase:
    def __init__(self, dsn: str, schema: str) -> None:
        self._pool: t.Optional[asyncpg.Pool] = None
        self._schema = schema
        self._dsn = dsn

    def initialize(self, bot: lb.BotApp):
        async def _(_: hk.StartedEvent):

            logging.info("initializing...")

            await self.connect()
            await self.create_schema()
            await self.initialize_guilds(bot.default_enabled_guilds)

            logging.info("done initializing.")

        return _

    async def initialize_guilds(self, guilds: t.Sequence[int]):
        for guild_id in guilds:
            await self.execute("INSERT INTO guilds VALUES ($1) ON CONFLICT DO NOTHING", guild_id)
            logging.info(f"initialized default guild id '{guild_id}'")

        logging.info("done initializing guilds")

    @asynccontextmanager
    async def acquire(self) -> t.AsyncIterator[asyncpg.Connection]:

        if not self._pool:

            raise Exception("database not connected.")

        async with self._pool.acquire() as conn:
            yield conn

    async def connect(self):

        self._pool = await asyncpg.create_pool(self._dsn)

        logging.info(f"created pool connection '{self._pool}'")

    async def create_schema(self):

        async with self.acquire() as conn:
            try:
                with open(self._schema, "r") as schema:
                    await conn.execute(schema.read())
                    logging.info(f"done creating schema from '{self._schema}' with '{conn}'.")

            except FileNotFoundError:
                logging.warn(f"failed schema execution, schema is not found from '{self._schema}'.")

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
