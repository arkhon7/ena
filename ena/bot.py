import os
import logging
import dotenv
import typing as t


import hikari as hk
import lightbulb as lb

from aiocache import Cache
from aiocache.plugins import TimingPlugin
from aiocache.plugins import HitMissRatioPlugin


# from ena.database import EnaDatabase
from plugins.embed_utils import embed_utils_plugin

dotenv.load_dotenv()
logging.basicConfig(level=logging.DEBUG)


def injectable(injector: t.Callable[[lb.BotApp], lb.BotApp]):
    """
    a decorator that converts a function into an injectable, this
    is used for organizing multiple dependencies in the bot.

    """

    def wrapper(func: t.Callable[[lb.BotApp], lb.BotApp]):
        def _(bot: lb.BotApp):

            return func(injector(bot))

        return _

    return wrapper


# INJECTIONS


@injectable
def default_plugins(bot: lb.BotApp):

    DEFAULT_PLUGINS = [embed_utils_plugin]

    for plugin in DEFAULT_PLUGINS:

        bot.add_plugin(plugin)

    return bot


@injectable
def default_listeners(bot: lb.BotApp):
    async def load_presence(_: hk.StartedEvent):

        await bot.update_presence(
            status=hk.Status.ONLINE,
            activity=hk.Activity(
                name="/help",
                type=hk.ActivityType.LISTENING,
            ),
        )

    bot.subscribe(hk.StartedEvent, load_presence)

    return bot


@injectable
def cache(bot: lb.BotApp):

    CACHE_MAPPING_KEY = "cache"
    CACHE = Cache(
        cache_class=Cache.MEMORY,
        plugins=[
            HitMissRatioPlugin(),
            TimingPlugin(),
        ],
    )

    bot.d[CACHE_MAPPING_KEY] = CACHE

    return bot


# @injectable
# def database(bot: lb.BotApp):

#     SCHEMA = "db/schema.psql"

#     DSN = os.getenv("DB_STRING") or "NONE"

#     DATABASE_MAPPING_KEY = "database"

#     DATABASE = EnaDatabase(dsn=DSN, schema=SCHEMA)

#     bot.d[DATABASE_MAPPING_KEY] = DATABASE

#     # event listeners
#     async def init(_: hk.StartingEvent):

#         database: EnaDatabase = bot.d[DATABASE_MAPPING_KEY]

#         await database.connect()
#         await database.create_schema()
#         await database.insert_default_guild_ids(bot.default_enabled_guilds)

#     async def add_guild(event: hk.GuildJoinEvent):

#         database: EnaDatabase = bot.d[DATABASE_MAPPING_KEY]
#         guild_id = event.guild_id

#         await database.execute("INSERT INTO guilds VALUES ($1)", event.guild_id)
#         logging.info("added guild '{}'".format(guild_id))

#     async def remove_guild(event: hk.GuildLeaveEvent):

#         database: EnaDatabase = bot.d[DATABASE_MAPPING_KEY]
#         guild_id = event.guild_id

#         await database.execute("DELETE FROM guilds WHERE id = $1", guild_id)
#         logging.info("removed guild '{}'".format(guild_id))

#     bot.subscribe(hk.StartingEvent, init)
#     bot.subscribe(hk.GuildJoinEvent, add_guild)
#     bot.subscribe(hk.GuildLeaveEvent, remove_guild)

#     return bot


# @database # no db (for now)
@cache
@default_plugins
@default_listeners
def enafied(bot: lb.BotApp) -> lb.BotApp:

    return bot


# run bot here
def run():
    TOKEN = os.getenv("TOKEN") or "NONE"

    DEFAULT_GUILDS = (
        957116703374979093,
        938374580244979764,
        938346141723033600,
    )

    INTENTS = (
        hk.Intents.ALL_PRIVILEGED
        | hk.Intents.DM_MESSAGE_REACTIONS
        | hk.Intents.GUILD_MESSAGE_REACTIONS
        | hk.Intents.GUILD_MESSAGES
        | hk.Intents.GUILD_MEMBERS
        | hk.Intents.GUILDS
    )

    bot = lb.BotApp(
        token=TOKEN,
        intents=INTENTS,
        default_enabled_guilds=DEFAULT_GUILDS,
    )

    ena = enafied(bot)

    ena.run()
