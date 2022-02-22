from .plugin import expr_eval_plugin

import lightbulb


def load(bot: lightbulb.BotApp):
    bot.add_plugin(expr_eval_plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(expr_eval_plugin)
