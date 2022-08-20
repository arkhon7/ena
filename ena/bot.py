import os
import logging


import hikari as hk
import lightbulb as lb

from aiocache import Cache
from aiocache.plugins import TimingPlugin
from aiocache.plugins import HitMissRatioPlugin


from ena.database import EnaDatabase
from ena.cache import EnaCache
from ena.decors import injectable


logging.basicConfig(level=logging.DEBUG)


TOKEN = os.getenv("TOKEN") or "NONE"

DSN = os.getenv("DB_STRING") or "NONE"

SCHEMA = "db/schema.psql"

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


@injectable
def default_plugins(bot: lb.BotApp):

    DEFAULT_PLUGINS = [
        "plugins.debug",
        "plugins.greet",
        "plugins.templater",
        "plugins.react_role",
    ]

    for plugin in DEFAULT_PLUGINS:
        bot.load_extensions(plugin)

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
def database(bot: lb.BotApp):

    SCHEMA = "db/schema.psql"
    DSN = os.getenv("DB_STRING") or "NONE"
    KEY = "database"

    DATABASE = EnaDatabase(dsn=DSN, schema=SCHEMA)

    bot.d[KEY] = DATABASE

    # event listeners
    async def init(_: hk.StartingEvent):

        database: EnaDatabase = bot.d[KEY]

        await database.connect()
        await database.create_schema()
        await database.insert_default_guild_ids(bot.default_enabled_guilds)

    async def add_guild(event: hk.GuildJoinEvent):

        database: EnaDatabase = bot.d[KEY]
        guild_id = event.guild_id

        await database.execute("INSERT INTO guilds VALUES ($1)", event.guild_id)
        logging.info("added guild '{}'".format(guild_id))

    async def remove_guild(event: hk.GuildLeaveEvent):
        database: EnaDatabase = bot.d.ENA_DATABASE
        guild_id = event.guild_id

        await database.execute("DELETE FROM guilds WHERE id = $1", guild_id)
        logging.info("removed guild '{}'".format(guild_id))

    bot.subscribe(hk.StartingEvent, init)
    bot.subscribe(hk.GuildJoinEvent, add_guild)
    bot.subscribe(hk.GuildLeaveEvent, remove_guild)

    return bot


@injectable
def cache(bot: lb.BotApp):

    KEY = "cache"
    CACHE = Cache(
        cache_class=EnaCache,
        plugins=[
            HitMissRatioPlugin(),
            TimingPlugin(),
        ],
    )

    bot.d[KEY] = CACHE

    return bot


@cache
@database
@default_plugins
@default_listeners
def ena(bot: lb.BotApp) -> lb.BotApp:

    return bot


# constructor
def build_bot() -> lb.BotApp:
    bot = lb.BotApp(
        token=TOKEN,
        intents=INTENTS,
        default_enabled_guilds=DEFAULT_GUILDS,
        banner="ena",
    )

    return ena(bot)
