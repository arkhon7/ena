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
@lb.command("test_cache", "testttt")
@lb.implements(lb.SlashCommand)
async def _test_cache(ctx: lb.SlashContext):
    cache: EnaCache = ctx.bot.d.ENA_CACHE

    cache_slice: dict = await cache.get(f"{ctx.guild_id}:{plugin.name}")
    if cache_slice:

        for _ in range(24):
            res = await cache.get("jma")
            print(res)
        print(cache.hit_miss_ratio)
        print(cache.profiling)
        await ctx.respond("asdad")

    else:
        cache_slice = {"jma": 123}

        await cache.set(f"{ctx.guild_id}:{plugin.name}", value=cache_slice, ttl=300)


@plugin.command
@lb.command("test_get_cache", "testttt")
@lb.implements(lb.SlashCommand)
async def _test_get_cache(ctx: lb.SlashContext):
    cache: EnaCache = ctx.bot.d.ENA_CACHE
    cache_slice: dict = await cache.get(f"{ctx.guild_id}:{plugin.name}")

    if cache_slice:

        await ctx.respond(cache_slice["jma"])
