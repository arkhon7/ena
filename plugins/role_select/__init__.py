import lightbulb

from .plugin import role_select
from .role import create_reaction_role_handler


GUILD_ID = 957116703374979093


def build_custom_reaction_role_handler(
    bot: lightbulb.BotApp,
):  # to be cached inside the bot instance for handling reaction events in plugin listeners
    roles = [
        {"emoji_name": "pink_verified_icon", "role_id": 995335085698076732},  # anime
        {"emoji_name": "purple_verified_icon", "role_id": 995564101902278736},  # gamer
        {"emoji_name": "blue_verified_icon", "role_id": 995335036490498198},  # music
        {"emoji_name": "orange_verified_icon", "role_id": 995335303927697510},  # meme
        {"emoji_name": "green_verified_icon", "role_id": 995338406139793408},  # study
    ]

    reaction_role_handler = create_reaction_role_handler(
        bot, guild_id=GUILD_ID, roles=roles, message_id=bot.d["reaction_message_id"]
    )
    return reaction_role_handler


def load(bot):
    bot.add_plugin(role_select)
    bot.d["reaction_role_handler"] = build_custom_reaction_role_handler(bot)


def unload(bot):
    bot.remove_plugin(role_select)