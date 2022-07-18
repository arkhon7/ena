import lightbulb


from pprint import pformat

plugin = lightbulb.Plugin("debug-plugin")


@plugin.command
@lightbulb.command(name="ping", description="pong!")
@lightbulb.implements(lightbulb.SlashCommand)
async def _ping(ctx: lightbulb.Context):
    await ctx.respond("pong!")


# @plugin.command
# @lightbulb.command(name="cache", description="check cache")
# @lightbulb.implements(lightbulb.SlashCommand)
# async def _cache(ctx: lightbulb.Context):

#     rrm_cache = ctx.bot.d.ReactionRoleMessages
#     rr_cache = ctx.bot.d.ReactionRoles

#     await ctx.respond(f"```{pformat(dict(reaction_role_messages=rrm_cache, reaction_roles=rr_cache))}```")
