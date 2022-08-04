import typing as t
import hikari as hk
import lightbulb as lb

# from ena.database import _load_database
# from ena.listeners import _on_starting

from ena.database import EnaDatabase


def mount_plugins(plugins: t.List[str]):
    """
    mounts plugins to the bot
    """

    def _func_wrap(func: t.Callable[[], lb.BotApp]):
        def _():

            bot = func()

            for plugin in plugins:
                bot.load_extensions(plugin)

            return bot

        return _

    return _func_wrap


def mount_database(dsn: str, schema: str):
    """
    mounts the database into lightbulb
    datastore

    """

    def _func_wrap(func: t.Callable[[], lb.BotApp]):
        def _():

            bot = func()
            bot.d.ENA_DATABASE = EnaDatabase(dsn, schema)
            bot.subscribe(hk.StartedEvent, bot.d.ENA_DATABASE.initialize(bot))

            return bot

        return _

    return _func_wrap
