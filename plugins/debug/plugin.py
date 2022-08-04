import hikari as hk
import lightbulb as lb


from ena.database import EnaDatabase


plugin = lb.Plugin("debug-plugin")


@plugin.command
@lb.command("test_db", "testttt")
@lb.implements(lb.SlashCommand)
async def _test_db(ctx: lb.SlashContext):
    database: EnaDatabase = ctx.bot.d.ENA_DATABASE

    await database.execute("SELECT * FROM emoji_role_pairs")

    await ctx.respond("asdad")
