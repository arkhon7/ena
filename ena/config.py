import os

import asyncio
import hikari


import lightbulb as lb
import typing as t

from ena.database import _load_database
from ena.listeners import _on_starting


# plugins
def load_plugins(func: t.Callable[[], lb.BotApp]):
    PLUGINS = [
        "plugins.debug",
        "plugins.utils",
        "plugins.react_role",
    ]

    def _():

        bot = func()

        for plugin in PLUGINS:
            bot.load_extensions(plugin)

        return bot

    return _


# database
def load_database(func: t.Callable[[], lb.BotApp]) -> t.Callable:

    DSN = os.getenv("DB_STRING")

    SCHEMA_PATH = "db/schema.psql"

    def _():
        bot = func()
        el = asyncio.get_event_loop()
        el.run_until_complete(_load_database(bot, DSN, SCHEMA_PATH))

        return bot

    return _


# cache
# maybe not needed (for now)

# def load_cache(func: t.Callable[[], lb.BotApp]) -> t.Callable:

#     CACHE = aiocache.Cache()

#     def _():
#         bot = func()
#         bot.d.CACHE = CACHE

#         return bot

#     return _


# listeners


def load_listeners(func: t.Callable[[], lb.BotApp]) -> t.Callable:
    def _():
        bot = func()

        bot.subscribe(hikari.StartedEvent, _on_starting(bot))

        return bot

    return _
