import lightbulb as lb
import hikari as hk

from .funcs import EmbedBuilder


embed_utils_plugin = lb.Plugin("embed-utils-plugin")


@embed_utils_plugin.command
@lb.command("embed", "make me create something!")
@lb.implements(lb.SlashCommandGroup)
async def embed_utils_group():
    pass


@embed_utils_group.child
@lb.option("url", "url of that will be bound to the title of the embed", required=False)
@lb.option("title", "title of the embed", required=False)
@lb.option("description", "description of the embed", required=False)
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
@lb.command("create", "create an embed", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def create_embed(ctx: lb.SlashContext):
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

    channel: hk.GuildChannel

    if ctx.options.show_author:

        builder.set_footer(
            text=f"by {ctx.user.username}#{ctx.user.discriminator}",
            icon=ctx.user.avatar_url,
        )

    try:
        if channel := ctx.options.channel:

            await ctx.bot.rest.create_message(channel.id, embed=builder.build())

        else:
            await ctx.bot.rest.create_message(ctx.channel_id, embed=builder.build())

        await ctx.respond("done!")

    except hk.BadRequestError:
        await ctx.respond("bad embed!")


# maybe use a dict approach instead of setting the embed builder instance
