import asyncpg

import logging

import typing as t
import hikari as hk
import lightbulb as lb

from contextlib import asynccontextmanager


logging = logging.getLogger(__name__)  # type:ignore


class EnaDatabase:
    def __init__(self, dsn: str, schema: t.Optional[str] = None) -> None:
        self._pool: t.Optional[asyncpg.Pool] = None
        self._schema: t.Optional[str] = schema
        self._dsn: str = dsn

    # bot listeners
    def _on_start(self, bot: lb.BotApp):
        async def _callback(_: hk.StartedEvent):

            logging.info("initializing...")

            await self.connect()
            await self.create_schema()
            await self.insert_default_guild_ids(bot.default_enabled_guilds)

        return _callback

    def _on_guild_join(self, bot: lb.BotApp):
        async def _callback(event: hk.GuildJoinEvent):
            guild_id = event.guild_id
            await self.execute("INSERT INTO guilds VALUES ($1)", guild_id)
            logging.info("added guild '{}'".format(guild_id))

        return _callback

    def _on_guild_leave(self, bot: lb.BotApp):
        async def _callback(event: hk.GuildLeaveEvent):
            guild_id = event.guild_id

            await self.execute("DELETE FROM guilds WHERE id = $1", guild_id)
            logging.info("removed guild '{}'".format(guild_id))

        return _callback

    async def insert_default_guild_ids(self, guilds: t.Sequence[int]):
        for guild_id in guilds:
            await self.execute("INSERT INTO guilds VALUES ($1) ON CONFLICT DO NOTHING", guild_id)
            logging.info("initialized default guild id '{}'".format(guild_id))

        logging.info("done.")

    # database controls
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

        if self._schema:
            async with self.acquire() as conn:
                try:
                    with open(self._schema, "r") as schema:
                        await conn.execute(schema.read())
                        logging.info(
                            "done creating schema from the given path '{}' with '{}'.".format(self._schema, conn)
                        )

                except FileNotFoundError:
                    logging.warn(
                        "failed schema creation, schema is not found from the given path '{}'.".format(self._schema)
                    )

        else:
            logging.info("no schema specified, skipping schema creation.")

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
