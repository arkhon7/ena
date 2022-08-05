import typing as t
import hikari as hk
import lightbulb as lb

from aiocache.serializers import BaseSerializer
from aiocache.plugins import BasePlugin
from aiocache import Cache

from ena.cache import EnaCache
from ena.database import EnaDatabase


class ListenerT(t.TypedDict):
    event_type: t.Type[hk.Event]
    callback: t.Callable[[lb.BotApp], t.Callable[[hk.Event], t.Any]]


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
            bot.subscribe(hk.StartedEvent, bot.d.ENA_DATABASE._on_start(bot))
            bot.subscribe(hk.GuildJoinEvent, bot.d.ENA_DATABASE._on_guild_join(bot))
            bot.subscribe(hk.GuildLeaveEvent, bot.d.ENA_DATABASE._on_guild_leave(bot))

            return bot

        return _

    return _func_wrap


def mount_listeners(listeners: t.List[ListenerT]):
    """
    mounts custom listeners, this uses `lightbulb.BotApp.subscribe` function.


    PARAMETERS
    ----------

    `listeners: ListenerT`

    A dict containing `'event_type'` and `'callback'` keys. The `'event_type'`
    is where the `hikari.Event` is specified, and the `'callback'` must be a
    synchronous method that takes `lightbulb.BotApp` as an argument and must
    return an async method that takes the `event_type`

    Example
    -------
    ```py
    def load_presence(bot: lightbulb.BotApp):
        async def _listener(event: hikari.StartedEvent)
            await bot.update_presence(...)
        return _listener

    @mount_listeners([
        {"event_type": hikari.StartedEvent, "callback": load_presence}
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
                bot.subscribe(listener["event_type"], listener["callback"](bot))

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
