import lightbulb
import hikari

plugin = lightbulb.Plugin("utility-plugin")


# this command must be moved to separate plugin (maybe utilities?) # TODO
@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("content", "your message content", required=False, type=hikari.OptionType.STRING, default=None)
@lightbulb.option("footer", "the footer of the embed.", required=False, type=hikari.OptionType.STRING, default=None)
@lightbulb.option("image", "the image of the embed.(link)", required=False, type=hikari.OptionType.STRING, default=None)
@lightbulb.option(
    "thumbnail", "the thumbnail of the embed.(link)", required=False, type=hikari.OptionType.STRING, default=None
)
@lightbulb.option("field_content", "content of the field.", required=False, type=hikari.OptionType.STRING, default=None)
@lightbulb.option("field_name", "name of the field.", required=False, type=hikari.OptionType.STRING, default=None)
@lightbulb.option("embed_color", "HEX COLOR", required=False, type=hikari.OptionType.STRING, default=None)
@lightbulb.option("user", "optional... user to DM this to", required=False, type=hikari.OptionType.USER, default=None)
@lightbulb.option(
    "description", "the description of the embed", required=False, type=hikari.OptionType.STRING, default=None
)
@lightbulb.option("title", "the title of the embed.", required=False, type=hikari.OptionType.STRING, default=None)
@lightbulb.option(
    "channel", "channel to send this message at", required=False, type=hikari.OptionType.CHANNEL, default=None
)
@lightbulb.command("create_rich_message", "lets you build a cool message!")
@lightbulb.implements(lightbulb.SlashCommand)
async def _create_rich_message(ctx: lightbulb.Context) -> None:

    embed = hikari.Embed()

    channel_id: int = ctx.channel_id
    content: str

    options = ctx.options

    # if options.content:
    #     content = options.content

    if options.channel:
        channel_id = options.channel

    if options.title:
        embed.title = options.title

    if options.description:
        embed.description = options.description

    if options.embed_color:
        embed.color = options.embed_color

    if options.field_name:
        embed.add_field(options.field_name, options.field_content)

    if options.set_thumbnail:
        embed.set_thumbnail(options.thumbnail)

    if options.image:
        embed.set_image(hikari.URL(options.image))

    if options.footer:
        embed.set_footer(options.footer)

    if options.user:
        new_dm_channel = await ctx.bot.rest.create_dm_channel(options.user)
        message = await ctx.bot.rest.create_message(content=options.content, channel=new_dm_channel, embed=embed)

    else:
        message = await ctx.bot.rest.create_message(content=options.content, channel=channel_id, embed=embed)

    await ctx.respond(f"Your message (id: {message.id}) has been created!", flags=hikari.MessageFlag.EPHEMERAL)


# @plugin.command
# @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
# @lightbulb.option("emoji", "emoji to convert", type=hikari.OptionType.STRING)
# @lightbulb.command("emoji_str", "convert emoji into a string!")
# @lightbulb.implements(lightbulb.SlashCommand)
# async def _emoji_str(ctx: lightbulb.SlashContext):
#     await ctx.respond("")
