import os
import dotenv
import logging


import hikari
import lightbulb as lb

from ena.decors import mount_database
from ena.decors import mount_plugins

dotenv.load_dotenv()
logging.basicConfig(level=logging.DEBUG)


TOKEN = os.getenv("TOKEN") or "NONE"


INTENTS = (
    hikari.Intents.ALL_PRIVILEGED
    | hikari.Intents.DM_MESSAGE_REACTIONS
    | hikari.Intents.GUILD_MESSAGE_REACTIONS
    | hikari.Intents.GUILD_MESSAGES
    | hikari.Intents.GUILD_MEMBERS
    | hikari.Intents.GUILDS
)

DEFAULT_GUILDS = (957116703374979093, 938374580244979764)
DSN = os.getenv("DB_STRING") or "NONE"
SCHEMA = "db/schema.psql"


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
