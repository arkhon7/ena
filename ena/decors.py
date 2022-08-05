import typing as t
import hikari as hk
import lightbulb as lb

from aiocache.serializers import BaseSerializer
from aiocache.plugins import BasePlugin
from aiocache import Cache

from ena.cache import EnaCache
from ena.database import EnaDatabase


def mount_plugins(plugins: t.List[str]):
    """
    mounts plugins to the bot

    PARAMETERS
    ----------

    `plugins: t.List[str]`

    List of module/package names. The plugin must have a `load`
    function in order for be read as a plugin.


    """

    def _func_wrap(func: t.Callable[[], lb.BotApp]):
        def _():

            bot = func()

            for plugin in plugins:
                bot.load_extensions(plugin)

            return bot

        return _

    return _func_wrap


def mount_database(dsn: str, schema: t.Optional[str] = None):
    """
    mounts the database to lb datastore and subscribes the necessary listeners
    into the bot. The database instance is accessed on `bot.d.ENA_DATABASE`

    PARAMETERS
    ----------

    `dsn: str`

    The database uri of the client

    `schema: str | None`

    The path for schema, if specified, this executes the schema when the bot
    starts


    """

    def _func_wrap(func: t.Callable[[], lb.BotApp]):
        def _():

            bot = func()
            bot.d.ENA_DATABASE = EnaDatabase(dsn, schema)

            return bot

        return _

    return _func_wrap


def mount_listeners(listeners: t.List[t.Callable[[lb.BotApp], t.Tuple[hk.Event, t.Callable[[hk.Event], t.Any]]]]):
    """
    mounts custom listeners, this uses `lightbulb.BotApp.subscribe` function.


    PARAMETERS
    ----------

    `listeners: ListenerT`

    List of functions that takes the `lightbulb.BotApp` as an argument and returns
    an event type and a callback

    Example
    -------
    ```py
    # Writing a listener function
    def load_presence(bot: lightbulb.BotApp):
        async def _callback(event: hikari.StartedEvent)
            await bot.update_presence(...)
        return hk.StartedEvent, _callback
    ...

    # mounting the listener function to the bot
    @mount_listeners([
        load_presence
    ])
    def build_bot():
        bot = lightbulb.BotApp(...)
        return bot
    ```
    """

    def _func_wrap(func: t.Callable[[], lb.BotApp]):
        def _():

            bot = func()

            for listener in listeners:
                event_type, callback = listener(bot)
                bot.subscribe(event_type, callback)

            return bot

        return _

    return _func_wrap


def mount_cache(
    serializer: t.Optional[BaseSerializer] = None,
    plugins: t.Optional[BasePlugin] = None,
    namespace: t.Optional[str] = None,
    timeout: t.Union[int, float] = 5,
):

    """
    mounts an `aiocache.Cache.MEMORY` instance to the datastore of the bot.
    The cache instance is accessed on `bot.d.ENA_CACHE`

    PARAMETERS
    ----------

    `serializer: aiocache.serializers.BaseSerializer | None`

    The serializer to be used in serializing cache

    `plugins: t.List[aiocache.plugins.BasePlugin] | None`

    The list of `BasePlugin` to be used in the cache

    `namespace: str | None`

    The namespace for the cache

    `timeout: int | float = 5`

    The timeout for cache operations
    """

    def _func_wrap(func: t.Callable[[], lb.BotApp]):
        def _():

            bot = func()
            bot.d.ENA_CACHE = Cache(
                cache_class=EnaCache,
                serializer=serializer,
                plugins=plugins,
                namespace=namespace,
                timeout=timeout,
            )

            return bot

        return _

    return _func_wrap
