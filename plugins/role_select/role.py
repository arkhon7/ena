import typing
import lightbulb


GUILD_ID = 957116703374979093


class ReactionRole:
    def __init__(
        self, bot: lightbulb.BotApp, role_id: int, emoji_name: str, message_id: int
    ) -> None:

        self.role_id = role_id
        self.emoji_name = emoji_name
        self.message_id = message_id
        self.bot = bot

    async def add_role_to_member(self, user_id: int, guild_id: int):
        await self.bot.rest.add_role_to_member(
            guild=guild_id, role=self.role_id, user=user_id
        )

    async def remove_role_from_member(self, user_id: int, guild_id: int):
        await self.bot.rest.remove_role_from_member(
            guild=guild_id, role=self.role_id, user=user_id
        )


class ReactionRoleHandler:
    def __init__(
        self,
        bot: lightbulb.BotApp,
        guild_id: int,
        message_id: int,
        reaction_roles: typing.List[ReactionRole],
    ) -> None:
        self.bot = bot
        self.guild_id = guild_id
        self.reaction_roles = reaction_roles
        self.message_id = message_id

    async def add_role_to_member(self, emoji_name: str, user_id: int):
        for reaction_role in self.reaction_roles:
            if (
                reaction_role.emoji_name == emoji_name
                and reaction_role.message_id == self.message_id
            ):
                await reaction_role.add_role_to_member(user_id, self.guild_id)

    async def remove_role_from_member(self, emoji_name: str, user_id: int):
        for reaction_role in self.reaction_roles:
            if (
                reaction_role.emoji_name == emoji_name
                and reaction_role.message_id == self.message_id
            ):
                await reaction_role.remove_role_from_member(user_id, self.guild_id)


def create_reaction_role(
    bot: lightbulb.BotApp, emoji_name: str, role_id: int, message_id: int
) -> ReactionRole:

    reaction_role = ReactionRole(bot, role_id, emoji_name, message_id)
    return reaction_role


def create_reaction_role_handler(
    bot: lightbulb.BotApp,
    guild_id: int,
    message_id: int,
    roles: typing.List[typing.Dict],
):

    reaction_roles: typing.List[ReactionRole] = list()

    for role in roles:
        reaction_roles.append(
            create_reaction_role(
                bot,
                role_id=role["role_id"],
                emoji_name=role["emoji_name"],
                message_id=message_id,
            )
        )

    role_handler = ReactionRoleHandler(
        bot, guild_id=guild_id, message_id=message_id, reaction_roles=reaction_roles
    )
    return role_handler
