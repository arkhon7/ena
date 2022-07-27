import asyncpg
import lightbulb
import hikari


from .controller import (
    fetch_all_reaction_role_awares,
    fetch_reaction_role_aware,
    delete_reaction_role_aware,
    insert_reaction_role_aware,
)


from .helpers import generate_message_link, parse_message_from_link

from .views import create_reaction_role_aware_pagination


plugin = lightbulb.Plugin("react-role", include_datastore=True)


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("rr", "manipulate reaction roles", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def reaction_group(ctx: lightbulb.Context):
    pass


@reaction_group.child
@lightbulb.option("link", "link of the message")
@lightbulb.command("create_aware", "adds reaction role awareness into a message!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _create_aware(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    message = parse_message_from_link(ctx.options.link)

    guild_id = message.guild_id
    channel_id = message.channel_id
    message_id = message.id

    await insert_reaction_role_aware(pool, message_id, channel_id, guild_id)

    await ctx.respond("Successfully created a new reaction-role aware message!")


@reaction_group.child
@lightbulb.option("id", "reaction role aware id")
@lightbulb.command("delete_aware", "removes reaction role awareness into a message!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _delete_aware(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL
    # guild_id = str(ctx.guild_id)

    await delete_reaction_role_aware(pool, ctx.options.id, ctx.guild_id)
    await ctx.respond("Successfully deleted a reaction-role aware message!")


@reaction_group.child
@lightbulb.option("id", "reaction role aware id")
@lightbulb.command("get_aware", "gets reaction role aware message from your guild by id!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _get_aware(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    rr_aware = await fetch_reaction_role_aware(pool, ctx.options.id)

    url = generate_message_link(rr_aware.guild_id, rr_aware.channel_id, rr_aware.message_id)
    embed = hikari.Embed(title="Here is your Reaction Role-Aware Message", url=url)

    await ctx.respond(embed=embed)


@reaction_group.child
@lightbulb.command("get_all_awares", "gets all reaction role aware messages from your guild!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _get_all_awares(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    if guild_id := ctx.guild_id:

        all_rr_awares = await fetch_all_reaction_role_awares(pool, guild_id)

        paginator = create_reaction_role_aware_pagination(all_rr_awares)

        await paginator.run(ctx)


# REACTION ROLE


# BULK COMMANDS


# setup test data
# @reaction_group.child
# @lightbulb.command(name="setup_test", description="initiate test setup", ephemeral=True)
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def _setup_test(ctx: lightbulb.SlashContext):
#     engine = ctx.bot.d.AsyncEngine
#     guild_id = str(ctx.guild_id)

#     # ROLES
#     GAMES_ROLE = "995564101902278736"
#     ANIME_ROLE = "995335085698076732"
#     MEMES_ROLE = "995335303927697510"

#     # EMOJIS
#     KOKO_RAGE_EMOJI_ID = "979224342762246184"
#     KOKO_CHILL_EMOJI_ID = "979223909981356093"
#     KOKO_CLAP_EMOJI_ID = "979225151566667807"

#     await insert_react_role(
#         engine,
#         emoji_id=KOKO_RAGE_EMOJI_ID,
#         emoji_name="koko_rage",
#         animated=True,
#         guild_id=guild_id,
#         role_id=GAMES_ROLE,
#     )

#     await insert_react_role(
#         engine,
#         emoji_id=KOKO_CHILL_EMOJI_ID,
#         emoji_name="koko_chill",
#         animated=True,
#         guild_id=guild_id,
#         role_id=ANIME_ROLE,
#     )

#     await insert_react_role(
#         engine,
#         emoji_id=KOKO_CLAP_EMOJI_ID,
#         emoji_name="koko_clap",
#         animated=True,
#         guild_id=guild_id,
#         role_id=MEMES_ROLE,
#     )

#     message = parse_message_from_link(
#         "https://discord.com/channels/957116703374979093/998595108482068621/1000047036416151594"
#     )

#     await insert_react_role_aware(engine, message.id, message.channel_id, message.guild_id)

#     await ctx.respond("DONE TEST SETUP")
