from .plugin import embed_utils_plugin


def load(bot):
    bot.add_plugin(embed_utils_plugin)


def unload(bot):
    bot.remove_plugin(embed_utils_plugin)
