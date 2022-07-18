import typing
import lightbulb
import hikari

from lightbulb.utils.pag import EmbedPaginator
from lightbulb.utils.nav import ButtonNavigator

from ena.cache import get_guild_cache, set_guild_cache, Cache
from plugins.role_select.views import create_roles_view
from .helpers import generate_message_link, generate_reaction_role_aware_id, generate_reaction_role_id
from .controller import (
    ReactionRoleAwareData,
    ReactionRoleData,
    add_reaction_role,
    add_reaction_role_aware,
    delete_reaction_role,
    fetch_all_reaction_role,
    fetch_all_reaction_role_aware,
    delete_reaction_role_aware,
)


plugin = lightbulb.Plugin("role-selection-plugin")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command(name="create_reaction_msg", description="create reaction message")
@lightbulb.implements(lightbulb.SlashCommand)
async def _create_reaction_message(ctx: lightbulb.Context):

    ROLES_CHANNEL_ID = 958156380559257660

    banner_embed = hikari.Embed(color="#36393f")
    banner_embed.set_image(hikari.URL("https://c.tenor.com/ACxZLKSQf8IAAAAC/ena-shinonome-ena.gif"))

    intro_embed = hikari.Embed(
        title=("**```            Role Selection           ```**"),
        description=(
            "Check out the roles that we have provided for you to have a customized feel on this server!\n\n"
            "**Disclaimer**: Each of the roles provided will unlock a certain category which will have another "
            "**roles (TODO)** channel for specifiying channels you want to see.\n"
        ),
        color="#36393f",
    )
    intro_embed.set_image(
        hikari.URL("https://cdn.discordapp.com/attachments/857365300966326292/879858842224185404/white2.png")
    )

    reaction_embed = hikari.Embed(
        title=("**```          Choose A Category         ```**"),
        description=(
            "<a:pink_verified_icon:995312808780644423> :: <@&995335085698076732>\n"
            "<a:purple_verified_icon:995312789419728916> :: <@&995564101902278736>\n"
            "<a:blue_verified_icon:995312743185911808> :: <@&995335036490498198>\n"
            "<a:orange_verified_icon:995337599067627570> :: <@&995335303927697510>\n"
            "<a:green_verified_icon:995312690522226708> :: <@&995338406139793408>\n"
        ),
        color="#36393f",
    )
    reaction_embed.set_image(
        hikari.URL("https://cdn.discordapp.com/attachments/857365300966326292/879858842224185404/white2.png")
    )

    await ctx.bot.rest.create_message(channel=ROLES_CHANNEL_ID, embed=banner_embed)
    await ctx.bot.rest.create_message(channel=ROLES_CHANNEL_ID, embed=intro_embed)
    reaction_message = await ctx.bot.rest.create_message(channel=ROLES_CHANNEL_ID, embed=reaction_embed)

    await reaction_message.add_reaction(emoji="pink_verified_icon", emoji_id=995312808780644423)
    await reaction_message.add_reaction(emoji="purple_verified_icon", emoji_id=995312789419728916)
    await reaction_message.add_reaction(emoji="blue_verified_icon", emoji_id=995312743185911808)
    await reaction_message.add_reaction(emoji="orange_verified_icon", emoji_id=995337599067627570)
    await reaction_message.add_reaction(emoji="green_verified_icon", emoji_id=995312690522226708)

    await ctx.respond("done creating the reaction message!")


# @plugin.listener(hikari.ReactionAddEvent)  # type: ignore
# async def handle_reaction_add(event: hikari.ReactionAddEvent):

#     reaction_role_handler = plugin.bot.d["reaction_role_handler"]
#     await reaction_role_handler.add_role_to_member(event.emoji_name, event.user_id)


# @plugin.listener(hikari.ReactionDeleteEvent)  # type: ignore
# async def handle_reaction_remove(event: hikari.ReactionDeleteEvent):

#     reaction_role_handler = plugin.bot.d["reaction_role_handler"]
#     await reaction_role_handler.remove_role_from_member(event.emoji_name, event.user_id)


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command(name="reactrole", description="manipulate reaction roles", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def reaction_group(ctx: lightbulb.Context):
    ...


@reaction_group.child
@lightbulb.option(name="message_id", description="target message's id", type=hikari.OptionType.STRING)
@lightbulb.command(name="mount", description="mounts reaction role awareness to a message", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _mount_reaction_role_aware(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    message_id = ctx.options.message_id
    channel_id = str(ctx.channel_id)
    guild_id = str(ctx.guild_id)

    rra_id = generate_reaction_role_aware_id(guild_id, channel_id, message_id)

    cached: typing.Optional[list[ReactionRoleAwareData]] = await get_guild_cache(
        guild_id=guild_id, key=Cache.REACTION_ROLE_AWARE
    )

    if cached:
        cached.append(ReactionRoleAwareData(id=rra_id, message_id=message_id, channel_id=channel_id, guild_id=guild_id))
        await set_guild_cache(guild_id=guild_id, key=Cache.REACTION_ROLE_AWARE, value=cached)

    # add reaction aware message data to db
    await add_reaction_role_aware(
        engine, rra_id=rra_id, guild_id=guild_id, channel_id=channel_id, message_id=message_id
    )

    await ctx.respond(
        "enabled reaction role message into this ! "
        f"You can now use `/rr add` with the `{rra_id}` to start adding reaction roles!",
    )


@reaction_group.child
@lightbulb.option(name="rra_id", description="target message's reaction role aware id", type=hikari.OptionType.STRING)
@lightbulb.command(
    name="unmount",
    description="unmounts reaction role awareness to a reaction role message (not undoable)",
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _unmount_reaction_role_aware(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    guild_id = str(ctx.guild_id)
    rra_id = ctx.options.rra_id

    cached: typing.Optional[list[ReactionRoleAwareData]] = await get_guild_cache(
        guild_id=guild_id, key=Cache.REACTION_ROLE_AWARE
    )

    if cached:
        for rra in cached:
            if rra.id == rra_id:
                cached.remove(rra)  # remove from cache

    # delete reaction aware message data to db
    await delete_reaction_role_aware(engine, rra_id=rra_id)
    await ctx.respond(
        f"deleted reaction role message (`{rra_id}`) from your server!",
    )


@reaction_group.child
@lightbulb.command(name="awares", description="fetches all reaction role aware messages", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _reaction_role_awares(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    guild_id = str(ctx.guild_id)

    cached: typing.Optional[list[ReactionRoleAwareData]] = await get_guild_cache(
        guild_id=guild_id, key=Cache.REACTION_ROLE_AWARE
    )

    if cached:
        results: typing.Optional[list[ReactionRoleAwareData]] = cached

    else:
        results = await fetch_all_reaction_role_aware(engine, guild_id)

    paginator = EmbedPaginator()

    if results:
        for i, data in enumerate(results):

            message_link = generate_message_link(
                message_id=data.message_id, channel_id=data.channel_id, guild_id=data.guild_id
            )

            rra_id_str = f"{i+1}. `{data.id}` [link]({message_link})"
            paginator.add_line(rra_id_str)

        navigator = ButtonNavigator(paginator.build_pages())
        await navigator.run(ctx)

        await set_guild_cache(guild_id=guild_id, key=Cache.REACTION_ROLE_AWARE, value=results)

    else:
        await ctx.respond("You don't have reaction role awares added yet!")


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
@lightbulb.command(name="create", description="create a new reaction role", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _create_reaction_role(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    emoji_name: str = ctx.options.emoji_name
    emoji_id: str = ctx.options.emoji_id
    role: hikari.Role = ctx.options.role
    role_id: str = str(role.id)

    guild_id = str(ctx.guild_id)

    rr_id = generate_reaction_role_id(guild_id=guild_id, emoji_id=emoji_id, emoji_name=emoji_name, role_id=role_id)

    cached: typing.Optional[typing.List[ReactionRoleData]] = await get_guild_cache(guild_id, key=Cache.REACTION_ROLE)

    if cached:
        # add the new reaction role into cache
        cached.append(
            ReactionRoleData(id=rr_id, role_id=role_id, emoji_id=emoji_id, emoji_name=emoji_name, guild_id=guild_id)
        )

    # add to db
    await add_reaction_role(
        engine, rr_id=rr_id, role_id=role_id, emoji_id=emoji_id, emoji_name=emoji_name, guild_id=guild_id
    )

    await ctx.respond(f"Added new reaction role `role: {rr_id}`")


@reaction_group.child
@lightbulb.option(name="rr_id", description="id of the reaction role to be deleted")
@lightbulb.command(name="delete", description="delete a new reaction role", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _delete_reaction_role(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine

    guild_id = str(ctx.guild_id)
    rr_id: str = ctx.options.rr_id

    cached: typing.Optional[typing.List[ReactionRoleData]] = await get_guild_cache(guild_id, key=Cache.REACTION_ROLE)
    if cached:
        # add the new reaction role into cache
        for rr in cached:
            if rr.id == rr_id:
                cached.remove(rr)

    # delete from db
    await delete_reaction_role(engine, rr_id=rr_id)

    await ctx.respond("Deleted")


@reaction_group.child
@lightbulb.command(name="all", description="get all reaction roles", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _fetch_all_reaction_role(ctx: lightbulb.SlashContext):
    engine = ctx.bot.d.AsyncEngine
    guild_id: str = str(ctx.guild_id)

    cached: typing.Optional[typing.List[ReactionRoleData]] = await get_guild_cache(guild_id, key=Cache.REACTION_ROLE)

    if cached:

        roles_view = create_roles_view(cached)
        await roles_view.run(ctx)

    else:
        results = await fetch_all_reaction_role(engine, guild_id=guild_id)

        if results:

            roles_view = create_roles_view(results)
            await roles_view.run(ctx)
            await set_guild_cache(guild_id=guild_id, key=Cache.REACTION_ROLE, value=results)

        else:
            await ctx.respond("You don't have reaction role awares added yet!")


@reaction_group.child
@lightbulb.command(name="reaction_role_id", description="get all reaction roles")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _establish_reaction_role_connection(ctx: lightbulb.SlashContext):
    # TODO
    ...


# TESTS


@reaction_group.child
@lightbulb.command(
    name="test_cache", description="unmounts reaction role awareness to a reaction role message (not undoable)"
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _test_cache(ctx: lightbulb.SlashContext):
    message_id = str(ctx.options.message_id)
    channel_id = str(ctx.channel_id)
    guild_id = str(ctx.guild_id)
    engine = ctx.bot.d.AsyncEngine
    engine = ctx.bot.d.AsyncEngine

    await add_reaction_role_aware(
        engine,
        rra_id="ebd25289aaf0efc72aa99da8182b3d77",
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id,
    )

    await add_reaction_role_aware(
        engine,
        rra_id="162658313a6e19270403f6f4f855e3e5",
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id,
    )

    await add_reaction_role_aware(
        engine,
        rra_id="afc8923b6a01b77411cfc5996b90968d",
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id,
    )

    await ctx.respond("Done test setup")
