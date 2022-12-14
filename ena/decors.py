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

    def wrapper(func: t.Callable[[lb.BotApp], lb.BotApp]):
        def _(bot: lb.BotApp):

            return func(injector(bot))

        return _

    return wrapper
