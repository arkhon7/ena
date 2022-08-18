import typing as t
import lightbulb as lb


def injectable(injector: t.Callable[[lb.BotApp], lb.BotApp]):
    """
    a decorator that converts a function into an injectable, this
    is used for organizing multiple dependencies in the bot.

    PARAMETER
    ---------

    `injector: t.Callable[[lb.BotApp], lb.BotApp]`

    A function with parameter `lightbulb.BotApp` and returns a
    `lightbulb.BotApp` instance

    EXAMPLE
    -------

    TODO
    """

    def main_wrapper(func: t.Callable[[lb.BotApp], lb.BotApp]):
        def _(bot: lb.BotApp):

            return func(injector(bot))

        return _

    return main_wrapper


def store(data: t.Dict[str, t.Any]):

    """
    a decorator that puts configs inside the bot's datastore. This
    must be used to a function that returns your bot instance if
    you're trying to inject a bot/plugin dependency

    PARAMETERS
    ----------

    `config: t.Dict[str, t.Any]`
    A dictionary with the key-value pairs of data

    EXAMPLE
    -------

    ```py
    @store({
        "API_KEY": os.getenv("API_KEY"),
    })
    def build_bot():

        return lightbulb.BotApp(...)
    ```

    """

    def _func_wrap(func: t.Callable[[lb.BotApp], lb.BotApp]):
        def _(bot: lb.BotApp):

            bot = func(bot)

            for key, value in data.items():

                bot.d[key] = value

            return bot

        return _

    return _func_wrap
