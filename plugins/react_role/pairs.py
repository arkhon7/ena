import asyncpg
import hikari
import lightbulb as lb

from .controller import add_pair
from .controller import delete_pair
from .controller import fetch_pair
from .controller import fetch_all_pairs_by_guild

from .models import EmojiRolePair


from ena.helpers import create_emoji_code, create_hash


@lb.option("role", "the role to pair with", type=hikari.OptionType.ROLE)
@lb.option("emoji_id", "the id of the emoji to pair with")
@lb.option("emoji_name", "name of the emoji to pair with")
@lb.option("is_animated", "whether or not the emoji used is animated", hikari.OptionType.BOOLEAN)
@lb.command("create_pair", "create an emoji-role pair for reaction roles in your guild", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _create_pair(ctx: lb.SlashContext):

    pool: asyncpg.Pool = ctx.bot.d.POOL
    role: hikari.Role = ctx.options.role
    emoji_id: int = int(ctx.options.emoji_id)
    emoji_name: str = ctx.options.emoji_name
    is_animated: bool = ctx.options.is_animated
    guild_id = ctx.guild_id

    id: str = create_hash(role.id, emoji_name, guild_id)

    if guild_id:

        await add_pair(
            pool,
            id,
            role.id,
            emoji_id,
            emoji_name,
            is_animated,
            guild_id,
        )

        await ctx.respond(f"Successfully added reaction role! **pair_id**:`{id}`")


@lb.option("id", "id of the emoji-role pair")
@lb.command("delete_pair", "delete an emoji-role pair from your guild", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _delete_pair(ctx: lb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL
    id: str = ctx.options.id

    if guild_id := ctx.guild_id:
        await delete_pair(pool, id, guild_id)

        await ctx.respond(f"Successfully deleted reaction role! **pair_id**:`{id}`")


@lb.option("id", "id of the emoji-role pair")
@lb.command("info", "get the info of a emoji-role pair", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _info_pair(ctx: lb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL
    id: str = ctx.options.id

    guild_id = ctx.guild_id

    if guild_id:
        record = await fetch_pair(pool, id, guild_id)

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


@lb.command("all_pairs", "get all emoji-role pairs from your guild", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def _all_pairs(ctx: lb.SlashContext):
    pool: asyncpg.Pool = ctx.bot.d.POOL

    guild_id = ctx.guild_id

    if guild_id:
        records = await fetch_all_pairs_by_guild(pool, guild_id)

        if records:
            pairs = [EmojiRolePair.from_dict(record) for record in records]

            pages = lb.utils.pag.EmbedPaginator()

            for i, pair in enumerate(pairs):
                emoji = create_emoji_code(pair.emoji_id, pair.emoji_name, pair.is_animated)
                role = f"<@&{pair.role_id}>"
                pages.add_line(f"{i} id:`{pair.id}`\nemoji:{emoji}\nrole:{role}")

            navigator = lb.utils.nav.ButtonNavigator(pages.build_pages())

            await navigator.run(ctx)
