import asyncpg
import hikari
import lightbulb as lb


def _on_starting(bot: lb.BotApp):
    async def _(_: hikari.StartedEvent):
        await bot.update_presence(
            status=hikari.Status.ONLINE,
            activity=hikari.Activity(
                name="/help",
                type=hikari.ActivityType.LISTENING,
            ),
        )

        await register_default_guild_ids(bot)

    return _


# listeners with dependencies
async def register_default_guild_ids(bot: lb.BotApp):
    conn: asyncpg.Connection
    pool: asyncpg.Pool = bot.d.POOL  # this will not work if database is not loaded yet
    if pool:
        async with pool.acquire() as conn:
            for guild_id in bot.default_enabled_guilds:
                await conn.execute("INSERT INTO guilds VALUES ($1) ON CONFLICT DO NOTHING", guild_id)
