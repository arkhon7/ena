import os
import dotenv
import logging


import hikari
import lightbulb as lb


from ena.config import load_plugins
from ena.config import load_database
from ena.config import load_listeners

dotenv.load_dotenv()
logging.basicConfig(level=logging.DEBUG)


TOKEN = os.getenv("TEST_TOKEN") or "NONE"


INTENTS = (
    hikari.Intents.ALL_PRIVILEGED
    | hikari.Intents.DM_MESSAGE_REACTIONS
    | hikari.Intents.GUILD_MESSAGE_REACTIONS
    | hikari.Intents.GUILD_MEMBERS
    | hikari.Intents.GUILDS
)

DEFAULT_GUILDS = (
    957116703374979093,
    938346141723033600,
    938374580244979764,
)


@load_listeners
@load_plugins
@load_database
def build_bot() -> lb.BotApp:

    bot = lb.BotApp(
        token=TOKEN,
        intents=INTENTS,
        default_enabled_guilds=DEFAULT_GUILDS,
    )

    return bot
