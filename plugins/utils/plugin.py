import lightbulb as lb
import hikari as hk


from .models import EmbedBuilder

plugin = lb.Plugin("suggest-plugin")


@plugin.command
@lb.command("create", "make me create something!")
@lb.implements(lb.SlashCommandGroup)
async def create_command():
    pass


@create_command.child
@lb.option("url", "url of that will be bound to the title of the embed", required=False)
@lb.option("title", "title of the embed", required=False)
@lb.option("description", "description of the embed", required=False)
@lb.option("color", "color of the embed", required=False)
@lb.option("image", "image of the embed", hk.OptionType.ATTACHMENT, required=False)
@lb.option("thumbnail", "thumbnail of the embed", hk.OptionType.ATTACHMENT, required=False)
@lb.command("embed", "create an embed")
@lb.implements(lb.SlashSubCommand)
async def _create_embed(ctx: lb.SlashContext):
    thumbnail: hk.Attachment
    image: hk.Attachment
    builder = EmbedBuilder()

    if url := ctx.options.url:
        builder.add_url(url)

    if title := ctx.options.title:
        builder.add_title(title)

    if description := ctx.options.description:
        builder.add_description(description)

    if color := ctx.options.color:
        builder.add_color(color)

    if image := ctx.options.image:

        img_bytes = await image.read()
        builder.add_image(img_bytes)

    if thumbnail := ctx.options.thumbnail:
        tn_bytes = await thumbnail.read()
        builder.add_thumbnail(tn_bytes)

    if (embed := builder.build()) is not None:

        embed.set_footer(
            text=f"made by {ctx.user.username}#{ctx.user.discriminator}",
            icon=ctx.user.avatar_url,
        )

        await ctx.respond(embed=embed)
