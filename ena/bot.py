import miru
import hikari
import lightbulb
import logging

import asyncio


import ena.config
import ena.db


# plugins
from plugins import PLUGINS

logging.basicConfig(level=logging.DEBUG)


def load_plugins(bot: lightbulb.BotApp):
    plugins = PLUGINS

    for plugin in plugins:
        try:
            bot.load_extensions(f"plugins.{plugin}")
        except lightbulb.ExtensionMissingLoad:
            logging.debug(f"plugins/{plugin} is not a plugin, skipping...")

    return bot


def load_presence(bot: lightbulb.BotApp):
    async def presence(_: hikari.StartedEvent):
        await bot.update_presence(
            status=hikari.Status.ONLINE,
            activity=hikari.Activity(
                name="/help",
                type=hikari.ActivityType.LISTENING,
            ),
        )

    bot.subscribe(hikari.StartedEvent, presence)


def load_database_engine(bot: lightbulb.BotApp):

    bot.d.AsyncEngine = ena.db.AsyncEngine

    return bot


def create_database_schema(bot: lightbulb.BotApp):
    logging.debug("Initiating migrations")

    engine = bot.d.AsyncEngine
    base = ena.db.Base

    logging.debug(base.metadata.__dict__)

    async def create_schema():
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)
            await conn.run_sync(base.metadata.create_all)

    asyncio.run(create_schema())


def build_bot() -> lightbulb.BotApp:

    TOKEN = ena.config.TOKEN
    if TOKEN:
        bot = lightbulb.BotApp(TOKEN, intents=hikari.Intents.ALL_PRIVILEGED)

    miru.load(bot)  # type: ignore

    load_database_engine(bot)
    load_plugins(bot)
    load_presence(bot)

    create_database_schema(bot)

    return bot
