import lightbulb
import hikari


from .controller import fetch_all_reaction_role_awares
from .controller import fetch_reaction_role_aware
from .controller import insert_react_role_aware
from .controller import delete_react_role_aware

from .controller import fetch_all_reaction_roles
from .controller import fetch_reaction_role
from .controller import insert_react_role
from .controller import delete_react_role

from .controller import insert_reaction_role_pair

from .helpers import parse_message_from_link

from .views import create_rr_aware_pagination
from .views import create_rr_pagination

plugin = lightbulb.Plugin("role-selection-plugin", include_datastore=True)


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command(name="rr", description="manipulate reaction roles", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def reaction_group(ctx: lightbulb.Context):
    pass


@reaction_group.child
@lightbulb.option("link", "link of the message")
@lightbulb.command(name="add_aware", description="adds reaction role awareness into a message!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _add_aware(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    message = parse_message_from_link(ctx.options.link)

    guild_id = message.guild_id
    channel_id = message.channel_id
    message_id = message.id

    await insert_react_role_aware(engine, message_id, channel_id, guild_id)

    await ctx.respond("Successfully created a new reaction-role aware message!")


@reaction_group.child
@lightbulb.option("id", "reaction role aware id")
@lightbulb.command(name="remove_aware", description="removes reaction role awareness into a message!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _remove_aware(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine
    guild_id = str(ctx.guild_id)

    await delete_react_role_aware(engine, ctx.options.id, guild_id)
    await ctx.respond("Successfully deleted a reaction-role aware message!")


@reaction_group.child
@lightbulb.option("id", "reaction role aware id")
@lightbulb.command(
    name="get_aware", description="gets reaction role aware message from your guild by id!", ephemeral=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _fetch_aware(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine
    guild_id = str(ctx.guild_id)

    rr_aware = await fetch_reaction_role_aware(engine, ctx.options.id, guild_id)
    if rr_aware:
        await ctx.respond(
            f"rr_aware_id: `{rr_aware.id}`"
            f"https://discord.com/channels/{rr_aware.guild_id}/{rr_aware.channel_id}/{rr_aware.message_id}"
        )


@reaction_group.child
@lightbulb.command(
    name="all_rr_awares", description="gets all reaction role aware messages from your guild!", ephemeral=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _fetch_all_awares(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine
    guild_id = str(ctx.guild_id)

    all_rr_awares = await fetch_all_reaction_role_awares(engine, guild_id)

    if all_rr_awares:

        all_rr_awares_view = create_rr_aware_pagination(all_rr_awares)

        await all_rr_awares_view.run(ctx)


# REACTION ROLE


@reaction_group.child
@lightbulb.option(
    name="emoji_name", description="name of the emoji to be used as a reaction role", type=hikari.OptionType.STRING
)
@lightbulb.option(
    name="emoji_id", description="id of the emoji to be used as a reaction role", type=hikari.OptionType.STRING
)
@lightbulb.option(
    name="role", description="role to be set onto the user upon reacting to the emoji", type=hikari.OptionType.ROLE
)
@lightbulb.option(
    name="animated",
    description="whether the emoji in use is animated or not",
    type=hikari.OptionType.BOOLEAN,
    required=False,
    default=False,
)
@lightbulb.command(name="create_react_role", description="create a reaction role!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _create_rrole(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    emoji_name: str = ctx.options.emoji_name
    emoji_id: str = ctx.options.emoji_id
    role: hikari.Role = ctx.options.role
    role_id: str = str(role.id)
    animated = ctx.options.animated

    guild_id = str(ctx.guild_id)

    await insert_react_role(engine, role_id, emoji_id, emoji_name, animated, guild_id)

    await ctx.respond("Added reaction role!")


@reaction_group.child
@lightbulb.option("id", "id of the reaction role to be deleted")
@lightbulb.command(name="delete_react_role", description="delete a reaction role!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _delete_rrole(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    id: str = ctx.options.id

    guild_id = str(ctx.guild_id)

    await delete_react_role(engine, id, guild_id)

    await ctx.respond("Deleted reaction role!")


@reaction_group.child
@lightbulb.option("id", "reaction role id")
@lightbulb.command(name="get_react_role", description="gets reaction role from your guild by id!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _fetch_rrole(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine
    guild_id = str(ctx.guild_id)

    rrole = await fetch_reaction_role(engine, ctx.options.id, guild_id)
    if rrole:
        await ctx.respond(f"{'a' if rrole.animated else ''}:{rrole.emoji_name}:{rrole.emoji_id}> <@&{rrole.role_id}>")


@reaction_group.child
@lightbulb.command(name="all_react_roles", description="gets all reaction roles from your guild!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _fetch_all_rrole(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine
    guild_id = str(ctx.guild_id)

    all_rroles = await fetch_all_reaction_roles(engine, guild_id)

    if all_rroles:
        roles_view = create_rr_pagination(all_rroles)

        await roles_view.run(ctx)


@reaction_group.child
@lightbulb.option(name="rr_id", description="id of the reaction role to be paired with reaction role aware message")
@lightbulb.option(
    name="rr_aware_id", description="id of the reaction role-aware message to be paired with the reaction role"
)
@lightbulb.command(
    name="create_pair", description="creates a pair of reaction role aware message and reaction role!", ephemeral=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _create_pair(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    guild_id = str(ctx.guild_id)

    rr_id = ctx.options.rr_id
    rr_aware_id = ctx.options.rr_aware_id

    rr = await fetch_reaction_role(engine, rr_id, guild_id)
    rr_aware = await fetch_reaction_role_aware(engine, rr_aware_id, guild_id)

    if rr and rr_aware:  # check if both are available
        await ctx.bot.rest.add_reaction(
            int(rr_aware.channel_id), int(rr_aware.message_id), rr.emoji_name, int(rr.emoji_id)
        )

        await insert_reaction_role_pair(engine, rr_id, rr_aware_id, guild_id)

        await ctx.respond(
            "Added reaction role to message https://discord.com/channels/"
            f"{rr_aware.guild_id}/{rr_aware.channel_id}/{rr_aware.message_id}"
        )


# TODO CREATE THE FETCH, FETCHALL, DELETE Methods for role pairings


@reaction_group.child
@lightbulb.command(name="setup_test", description="initiate test setup", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _setup_test(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine
    guild_id = str(ctx.guild_id)

    # ROLES
    GAMES_ROLE = "995564101902278736"
    ANIME_ROLE = "995335085698076732"
    MEMES_ROLE = "995335303927697510"

    # EMOJIS
    KOKO_RAGE_EMOJI_ID = "979224342762246184"
    KOKO_CHILL_EMOJI_ID = "979223909981356093"
    KOKO_CLAP_EMOJI_ID = "979225151566667807"

    await insert_react_role(
        engine,
        emoji_id=KOKO_RAGE_EMOJI_ID,
        emoji_name="koko_rage",
        animated=True,
        guild_id=guild_id,
        role_id=GAMES_ROLE,
    )

    await insert_react_role(
        engine,
        emoji_id=KOKO_CHILL_EMOJI_ID,
        emoji_name="koko_chill",
        animated=True,
        guild_id=guild_id,
        role_id=ANIME_ROLE,
    )

    await insert_react_role(
        engine,
        emoji_id=KOKO_CLAP_EMOJI_ID,
        emoji_name="koko_clap",
        animated=True,
        guild_id=guild_id,
        role_id=MEMES_ROLE,
    )

    message = parse_message_from_link(
        "https://discord.com/channels/957116703374979093/998595108482068621/1000047036416151594"
    )

    await insert_react_role_aware(engine, message.id, message.channel_id, message.guild_id)

    await ctx.respond("DONE TEST SETUP")
