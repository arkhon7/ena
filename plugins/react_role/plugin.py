import hikari
import lightbulb as lb
from ena.cache import EnaCache

from ena.database import EnaDatabase


from .controller import add_active_pair
from .controller import delete_active_pair
from .controller import delete_all_active_pairs_by_message
from .controller import fetch_all_active_pairs_by_message

from .controller import add_pair
from .controller import delete_pair
from .controller import fetch_pair
from .controller import fetch_all_pairs

from .models import ActiveEmojiRolePair
from .models import EmojiRolePair


from ena.helpers import create_emoji_code
from ena.helpers import create_hash
from ena.helpers import parse_message_from_link

plugin = lb.Plugin("reaction-role-plugin", include_datastore=True)


@plugin.command
@lb.command("react_role", "reactrole command group")
@lb.implements(lb.SlashCommandGroup)
async def react_role():
    pass


@react_role.child
@lb.option("role", "the role to pair with", type=hikari.OptionType.ROLE)
@lb.option("emoji_id", "the id of the emoji to pair with")
@lb.option("emoji_name", "name of the emoji to pair with")
@lb.option("is_animated", "whether or not the emoji used is animated", hikari.OptionType.BOOLEAN)
@lb.command("create_pair", "create an emoji-role pair for reaction roles in your guild", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _create_pair(ctx: lb.SlashContext):
    cache: EnaCache = ctx.bot.d.ENA_CACHE

    cache.hit_miss_ratio

    database: EnaDatabase = ctx.bot.d.ENA_DATABASE
    role: hikari.Role = ctx.options.role
    emoji_id: int = int(ctx.options.emoji_id)
    emoji_name: str = ctx.options.emoji_name
    is_animated: bool = ctx.options.is_animated
    guild_id = ctx.guild_id

    id: str = create_hash(role.id, emoji_name, guild_id)

    if guild_id:

        await add_pair(
            database,
            id,
            role.id,
            emoji_id,
            emoji_name,
            is_animated,
            guild_id,
        )

        await ctx.respond(f"Successfully added reaction role! **pair_id**:`{id}`")


@react_role.child
@lb.option("id", "id of the emoji-role pair")
@lb.command("delete_pair", "delete an emoji-role pair from your guild", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _delete_pair(ctx: lb.SlashContext):
    database: EnaDatabase = ctx.bot.d.ENA_DATABASE
    id: str = ctx.options.id

    if guild_id := ctx.guild_id:
        await delete_pair(database, id, guild_id)

        await ctx.respond(f"Successfully deleted reaction role! **pair_id**:`{id}`")


@react_role.child
@lb.option("id", "id of the emoji-role pair")
@lb.command("info", "get the info of a emoji-role pair", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _info_pair(ctx: lb.SlashContext):
    database: EnaDatabase = ctx.bot.d.ENA_DATABASE
    id: str = ctx.options.id

    guild_id = ctx.guild_id

    if guild_id:
        record = await fetch_pair(database, id, guild_id)

        if record:
            emoji_role_pair = EmojiRolePair.from_dict(record)

            embed = hikari.Embed(title="Here is your requested emoji-role pair")
            embed.add_field("id", emoji_role_pair.id)
            embed.add_field("role", f"<@&{emoji_role_pair.role_id}>")
            embed.add_field(
                "emoji",
                create_emoji_code(
                    emoji_role_pair.emoji_id,
                    emoji_role_pair.emoji_name,
                    emoji_role_pair.is_animated,
                ),
            )

            await ctx.respond(embed=embed)

        else:
            await ctx.respond("Cannot find this emoji-role pair!")


@react_role.child
@lb.command("all_pairs", "get all emoji-role pairs from your guild", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _all_pairs(ctx: lb.SlashContext):
    database: EnaDatabase = ctx.bot.d.ENA_DATABASE

    guild_id = ctx.guild_id

    if guild_id:
        records = await fetch_all_pairs(database, guild_id)

        if records:
            pairs = [EmojiRolePair.from_dict(record) for record in records]

            pages = lb.utils.pag.EmbedPaginator()

            for i, pair in enumerate(pairs):
                emoji = create_emoji_code(pair.emoji_id, pair.emoji_name, pair.is_animated)
                role = f"<@&{pair.role_id}>"
                pages.add_line(f"{i}. id:`{pair.id}` :: {emoji} :: {role}")

            navigator = lb.utils.nav.ButtonNavigator(pages.build_pages())

            await navigator.run(ctx)


# ADD/REMOVE ROLE TO MESSAGE
@react_role.child
@lb.option("id", "id of the emoji-role pair")
@lb.option("link", "link of the message")
@lb.command("mount", "mount an emoji-role pair to your message", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _mount_pair_to_message(ctx: lb.SlashContext):
    database: EnaDatabase = ctx.bot.d.ENA_DATABASE
    pair_id: str = ctx.options.id
    link = ctx.options.link
    guild_id = ctx.guild_id

    message = parse_message_from_link(link)

    if guild_id:
        record = await fetch_pair(database, pair_id, guild_id)

        if record:

            pair = EmojiRolePair.from_dict(record)
            # new active pair

            id = create_hash(pair.role_id, pair.emoji_name, message.message_id)

            await add_active_pair(
                database,
                id,
                pair.id,
                message.message_id,
                message.channel_id,
                message.guild_id,
            )

            await ctx.bot.rest.add_reaction(
                message.channel_id,
                message.message_id,
                pair.emoji_name,
                pair.emoji_id,
            )

            await ctx.respond("Successfully added reaction role!")


@react_role.child
@lb.option("id", "id of the active emoji-role pair")
@lb.option("link", "link of the message")
@lb.command("unmount", "unmount an emoji-role pair from a message", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _unmount_pair_to_message(ctx: lb.SlashContext):
    database: EnaDatabase = ctx.bot.d.ENA_DATABASE
    pair_id: str = ctx.options.id
    link = ctx.options.link
    guild_id = ctx.guild_id

    message = parse_message_from_link(link)

    if guild_id:
        record = await fetch_pair(database, pair_id, guild_id)
        if record:
            pair = EmojiRolePair.from_dict(record)
            # new active pair
            id = create_hash(pair.role_id, pair.emoji_name, message.message_id)
            await delete_active_pair(
                database,
                id,
                message.message_id,
                message.channel_id,
                message.guild_id,
            )

            await ctx.respond("Successfully deleted reaction role!")


# LISTENERS
@plugin.listener(hikari.GuildReactionAddEvent)
async def _handle_add_reaction(event: hikari.GuildReactionAddEvent):
    database: EnaDatabase = plugin.bot.d.ENA_DATABASE

    if app := plugin.bot.application:
        if event.user_id != app.id:
            records = await fetch_all_active_pairs_by_message(
                database,
                event.message_id,
                event.guild_id,
            )

            if records:
                active_pairs = [ActiveEmojiRolePair.from_dict(record) for record in records]

                for active_pair in active_pairs:
                    if active_pair.emoji_name == event.emoji_name and active_pair.message_id == event.message_id:
                        await plugin.bot.rest.add_role_to_member(
                            event.guild_id,
                            event.user_id,
                            active_pair.role_id,
                        )


@plugin.listener(hikari.GuildReactionDeleteEvent)
async def _handle_delete_reaction(event: hikari.GuildReactionDeleteEvent):
    database: EnaDatabase = plugin.bot.d.ENA_DATABASE

    records = await fetch_all_active_pairs_by_message(
        database,
        event.message_id,
        event.guild_id,
    )

    if records:

        active_pairs = [ActiveEmojiRolePair.from_dict(record) for record in records]

        for active_pair in active_pairs:
            if active_pair.emoji_name == event.emoji_name and active_pair.message_id == event.message_id:
                await plugin.bot.rest.remove_role_from_member(
                    event.guild_id,
                    event.user_id,
                    active_pair.role_id,
                )


@plugin.listener(hikari.GuildMessageDeleteEvent)
async def _handle_delete_message(event: hikari.GuildMessageDeleteEvent):
    database: EnaDatabase = plugin.bot.d.ENA_DATABASE

    await delete_all_active_pairs_by_message(
        database,
        event.message_id,
        event.channel_id,
        event.guild_id,
    )


@plugin.listener(hikari.GuildReactionDeleteAllEvent)
async def _handle_delete_all_reaction(event: hikari.GuildReactionDeleteAllEvent):
    database: EnaDatabase = plugin.bot.d.ENA_DATABASE

    await delete_all_active_pairs_by_message(
        database,
        event.message_id,
        event.channel_id,
        event.guild_id,
    )
