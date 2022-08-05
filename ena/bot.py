import os
import dotenv
import logging


import hikari as hk
import lightbulb as lb


from aiocache.plugins import HitMissRatioPlugin
from aiocache.plugins import TimingPlugin
from ena.database import EnaDatabase

from ena.decors import mount_cache, mount_listeners
from ena.decors import mount_database
from ena.decors import mount_plugins

dotenv.load_dotenv()
logging.basicConfig(level=logging.DEBUG)


TOKEN = os.getenv("TOKEN") or "NONE"

DSN = os.getenv("DB_STRING") or "NONE"
SCHEMA = "db/schema.psql"

DEFAULT_GUILDS = (957116703374979093, 938374580244979764)

INTENTS = (
    hk.Intents.ALL_PRIVILEGED
    | hk.Intents.DM_MESSAGE_REACTIONS
    | hk.Intents.GUILD_MESSAGE_REACTIONS
    | hk.Intents.GUILD_MESSAGES
    | hk.Intents.GUILD_MEMBERS
    | hk.Intents.GUILDS
)


def _load_presence(bot: lb.BotApp):
    async def _callback(_: hk.StartedEvent):

        await bot.update_presence(
            status=hk.Status.ONLINE,
            activity=hk.Activity(
                name="/help",
                type=hk.ActivityType.LISTENING,
            ),
        )

    return _callback


def _on_start(bot: lb.BotApp):
    database: EnaDatabase = bot.d.ENA_DATABASE

    async def _callback(_: hk.StartedEvent):

        logging.info("initializing...")

        await database.connect()
        await database.create_schema()
        await database.insert_default_guild_ids(bot.default_enabled_guilds)

    return _callback


def _on_guild_join(bot: lb.BotApp):
    database: EnaDatabase = bot.d.ENA_DATABASE

    async def _callback(event: hk.GuildJoinEvent):
        guild_id = event.guild_id
        await database.execute("INSERT INTO guilds VALUES ($1)", guild_id)
        logging.info("added guild '{}'".format(guild_id))

    return _callback


def _on_guild_leave(bot: lb.BotApp):
    database: EnaDatabase = bot.d.ENA_DATABASE

    async def _callback(event: hk.GuildLeaveEvent):
        guild_id = event.guild_id

        await database.execute("DELETE FROM guilds WHERE id = $1", guild_id)
        logging.info("removed guild '{}'".format(guild_id))

    return _callback


@mount_listeners(
    listeners=[
        {"event_type": hk.StartedEvent, "callback": _load_presence},  # make this into a class
        {"event_type": hk.StartedEvent, "callback": _on_start},
        {"event_type": hk.GuildJoinEvent, "callback": _on_guild_join},
        {"event_type": hk.GuildLeaveEvent, "callback": _on_guild_leave},
    ],
)
@mount_cache(
    plugins=[
        HitMissRatioPlugin(),
        TimingPlugin(),
    ],
    namespace="enabot:",
)
@mount_plugins(
    plugins=[
        "plugins.debug",
        "plugins.greet",
        "plugins.react_role",
    ]
)
@mount_database(
    dsn=DSN,
    schema=SCHEMA,
)
def build_bot() -> lb.BotApp:

    bot = lb.BotApp(
        token=TOKEN,
        intents=INTENTS,
        default_enabled_guilds=DEFAULT_GUILDS,
    )

    return bot
