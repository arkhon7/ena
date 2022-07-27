import lightbulb

plugin = lightbulb.Plugin("debug-plugin")


@plugin.command
@lightbulb.command(name="ping", description="pong!")
@lightbulb.implements(lightbulb.SlashCommand)
async def _ping(ctx: lightbulb.Context):
    await ctx.respond("pong!")


@plugin.command
@lightbulb.command(name="datastore", description="pong!")
@lightbulb.implements(lightbulb.SlashCommand)
async def _datastore(ctx: lightbulb.Context):
    await ctx.respond(ctx.bot.d)
