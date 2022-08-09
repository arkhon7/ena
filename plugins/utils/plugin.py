import lightbulb as lb
import hikari as hk


from .models import EmbedBuilder

plugin = lb.Plugin("utility-plugin")


@plugin.command
@lb.command("create", "make me create something!")
@lb.implements(lb.SlashCommandGroup)
async def create_command():
    pass


# @create_command.child
# @lb.option("channel", "channel to send the embed", hk.OptionType.CHANNEL, required=False)
# @lb.option("render", "whether you want the url to be rendered as image or thumbnail", choices=["thumbnail", "image"])
# @lb.command("banner_embed", "create an embed with server banner as image")
# @lb.implements(lb.SlashSubCommand)
# async def _create_banner_embed(ctx: lb.SlashContext):

#     guild: t.Optional[hk.Guild] = ctx.get_guild()

#     embed = hk.Embed()
#     if guild:

#         if ctx.options.render == "thumbnail":
#             embed.set_thumbnail(guild.banner_url)

#         elif ctx.options.render == "thumbnail":
#             embed.set_image(guild.banner_url)

#     if channel := ctx.options.channel:
#         await ctx.bot.rest.create_message(channel.id, embed=embed)

#     else:
#         await ctx.bot.rest.create_message(ctx.channel_id, embed=embed)


# @create_command.child
# @lb.option("channel", "channel to send the embed", hk.OptionType.CHANNEL, required=False)
# @lb.option("render", "whether you want the url to be rendered as image or thumbnail", choices=["thumbnail", "image"])
# @lb.command("icon_embed", "create an embed with server icon as image")
# @lb.implements(lb.SlashSubCommand)
# async def _create_icon_embed(ctx: lb.SlashContext):

#     guild: t.Optional[hk.Guild] = ctx.get_guild()

#     embed = hk.Embed()
#     if guild:
#         if ctx.options.render == "thumbnail":
#             embed.set_thumbnail(guild.icon_url)

#         elif ctx.options.render == "thumbnail":
#             embed.set_image(guild.icon_url)

#     if channel := ctx.options.channel:
#         await ctx.bot.rest.create_message(channel.id, embed=embed)

#     else:
#         await ctx.bot.rest.create_message(ctx.channel_id, embed=embed)


@create_command.child
@lb.option("url", "url of that will be bound to the title of the embed", required=False)
@lb.option("title", "title of the embed", required=False)
@lb.option("description", "description of the embed", required=False)
@lb.option("description_file", "text file for description", hk.OptionType.ATTACHMENT, required=False)
@lb.option("color", "color of the embed", required=False)
@lb.option("image", "image of the embed", hk.OptionType.ATTACHMENT, required=False)
@lb.option("image_url", "image url of the embed", required=False)
@lb.option("thumbnail", "thumbnail of the embed", hk.OptionType.ATTACHMENT, required=False)
@lb.option("thumbnail_url", "thumbnail url of the embed", required=False)
@lb.option(
    "show_author",
    "whether or not the embed will display the author of the embed",
    hk.OptionType.BOOLEAN,
    required=False,
    default=True,
)
@lb.option("channel", "channel to send the embed", hk.OptionType.CHANNEL, required=False)
@lb.command("embed", "create an embed")
@lb.implements(lb.SlashSubCommand)
async def _create_embed(ctx: lb.SlashContext):
    thumbnail: hk.Attachment
    image: hk.Attachment
    description_file: hk.Attachment
    builder = EmbedBuilder()

    if url := ctx.options.url:
        builder.add_url(url)

    if title := ctx.options.title:
        builder.add_title(title)

    if description := ctx.options.description:

        builder.add_description(description)

    if description_file := ctx.options.description_file:

        text_bytes = await description_file.read()
        builder.add_description(text_bytes.decode())

    if color := ctx.options.color:
        builder.add_color(color)

    if image := ctx.options.image:

        img_bytes = await image.read()
        builder.add_image(img_bytes)

    if image_url := ctx.options.image_url:
        builder.add_image(hk.URL(image_url))

    if thumbnail := ctx.options.thumbnail:
        tn_bytes = await thumbnail.read()
        builder.add_thumbnail(tn_bytes)

    if thumbnail_url := ctx.options.thumbnail_url:

        builder.add_thumbnail(hk.URL(thumbnail_url))

    if (embed := builder.build()) is not None:

        channel: hk.GuildChannel

        if ctx.options.show_author:

            embed.set_footer(
                text=f"by {ctx.user.username}#{ctx.user.discriminator}",
                icon=ctx.user.avatar_url,
            )

        if channel := ctx.options.channel:
            await ctx.bot.rest.create_message(channel.id, embed=embed)

        else:
            await ctx.bot.rest.create_message(ctx.channel_id, embed=embed)

    else:
        await ctx.respond("Please put at least one info in the embed!", flags=hk.MessageFlag.EPHEMERAL)
