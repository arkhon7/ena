import asyncpg
import lightbulb
import hikari


from .controller import (
    fetch_all_reaction_role_awares,
    fetch_all_reaction_roles,
    fetch_reaction_role_aware,
    fetch_reaction_role,
    insert_reaction_role_aware,
    insert_reaction_role,
    delete_reaction_role_aware,
    delete_reaction_role,
)


from .helpers import generate_message_link, parse_message_from_link

from .views import create_reaction_role_aware_pagination
from .views import create_reaction_role_pagination


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

    await insert_reaction_role_aware(
        pool,
        message_id,
        channel_id,
        guild_id,
    )

    await ctx.respond("Successfully created a new reaction-role aware message!")


@reaction_group.child
@lightbulb.option("id", "reaction role aware id", required=True)
@lightbulb.command("delete_aware", "removes reaction role awareness into a message!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _delete_aware(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL
    # guild_id = str(ctx.guild_id)

    await delete_reaction_role_aware(pool, ctx.options.id, ctx.guild_id)
    await ctx.respond("Successfully deleted a reaction-role aware message!")


@reaction_group.child
@lightbulb.option("id", "reaction role aware id", required=True)
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
@reaction_group.child
@lightbulb.option("role", "role to be assigned when reacting", hikari.OptionType.ROLE, required=True)
@lightbulb.option("emoji_id", "id of emoji to use in reaction role", required=True)
@lightbulb.option("emoji_name", "name of emoji to use in reaction role", required=True)
@lightbulb.option("animated", "whether the emoji in use is animated", hikari.OptionType.BOOLEAN, required=True)
@lightbulb.command("create_reaction_role", "create a reaction_role!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _create_reaction_role(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    role: hikari.Role = ctx.options.role
    emoji_id = int(ctx.options.emoji_id)
    emoji_name = ctx.options.emoji_name
    animated = ctx.options.animated
    guild_id = ctx.guild_id

    await insert_reaction_role(
        pool,
        role.id,
        emoji_id,
        emoji_name,
        animated,
        guild_id,
    )

    # make this a func
    if animated:
        emoji = f"<a:{emoji_name}:{emoji_id}>"
    else:
        emoji = f"<:{emoji_name}:{emoji_id}>"
    #

    await ctx.respond(f"Added new reaction role ({emoji}) to your server!")


@reaction_group.child
@lightbulb.option("id", "reaction role id", required=True)
@lightbulb.command("delete_reaction_role", "deletes a reaction role from your server!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _delete_reaction_role(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    await delete_reaction_role(pool, ctx.options.id, ctx.guild_id)
    await ctx.respond("Successfully deleted a reaction role!")


@reaction_group.child
@lightbulb.option("id", "reaction role id", required=True)
@lightbulb.command("get_reaction_role", "get the reaction role info", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _get_reaction_role(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    reaction_role = await fetch_reaction_role(pool, ctx.options.id)

    embed = hikari.Embed(title="Here is your Reaction Role")
    embed.add_field("id", reaction_role.id)
    embed.add_field("role", f"<@&{reaction_role.role_id}>")

    if reaction_role.animated:
        emoji = f"<a:{reaction_role.emoji_name}:{reaction_role.emoji_id}>"
    else:
        emoji = f"<:{reaction_role.emoji_name}:{reaction_role.emoji_id}>"

    embed.add_field("emoji", emoji)

    await ctx.respond(embed=embed)


@reaction_group.child
@lightbulb.command("get_all_reaction_roles", "gets all reaction roles from your server!", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _get_all_reaction_roles(ctx: lightbulb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    all_reaction_roles = await fetch_all_reaction_roles(pool, ctx.guild_id)

    if all_reaction_roles:
        paginator = create_reaction_role_pagination(all_reaction_roles)

        await paginator.run(ctx)
