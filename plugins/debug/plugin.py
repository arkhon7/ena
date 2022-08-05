import hikari as hk
import lightbulb as lb

from ena.cache import EnaCache
from ena.database import EnaDatabase


plugin = lb.Plugin("debug-plugin")


@plugin.command
@lb.command("test_db", "testttt")
@lb.implements(lb.SlashCommand)
async def _test_db(ctx: lb.SlashContext):
    database: EnaDatabase = ctx.bot.d.ENA_DATABASE

    await database.execute("SELECT * FROM emoji_role_pairs")

    await ctx.respond("asdad")


@plugin.command
@lb.command("test_cache", "testttt", auto_defer=True)
@lb.implements(lb.SlashCommand)
async def _test_cache(ctx: lb.SlashContext):
    cache: EnaCache = ctx.bot.d.ENA_CACHE

    await cache.set("jma", 123)

    for _ in range(10000):
        await cache.get("jma")
    print(cache.hit_miss_ratio)
    print(cache.profiling)
    await ctx.respond("asdad")
