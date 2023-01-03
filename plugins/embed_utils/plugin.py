import lightbulb as lb
import hikari as hk

from paintcord import compile

from ena.helpers import parse_message_ref


embed_utils_plugin = lb.Plugin("embed-utils-plugin")


@embed_utils_plugin.command
@lb.command("embed", "make me create something!")
@lb.implements(lb.SlashCommandGroup)
async def embed_utils_group():
    pass


@embed_utils_group.child
@lb.option("template", "ena template", hk.OptionType.ATTACHMENT)
@lb.option("link", "this will edit the message on the given link", required=False)
@lb.option("channel", "channel to send the template to", hk.OptionType.CHANNEL, required=False)
@lb.command("template", "create embeds from template", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def create_from_template(ctx: lb.SlashContext):

    raw_template: hk.Attachment = ctx.options.template
    channel: hk.GuildChannel

    template = await raw_template.read()

    req_body = compile(template.decode())

    msg_body = req_body[0]

    embed_bodies = msg_body["embeds"]

    embeds = []

    for embed_body in embed_bodies:

        embeds.append(ctx.bot.entity_factory.deserialize_embed(embed_body))

    if message_link := ctx.options.message_link:

        msg_ref = parse_message_ref(message_link)

        await ctx.bot.rest.edit_message(
            msg_ref.channel_id, msg_ref.message_id, content=msg_body["content"], embeds=embeds
        )

    else:
        if channel := ctx.options.channel:

            await ctx.bot.rest.create_message(channel.id, content=msg_body["content"], embeds=embeds)

        else:

            await ctx.bot.rest.create_message(ctx.channel_id, content=msg_body["content"], embeds=embeds)

    await ctx.respond("Done creating from template!")


@embed_utils_group.child
@lb.option("content", "content of the message", hk.OptionType.STRING, required=False)
@lb.option("url", "url of that will be bound to the title of the embed", hk.OptionType.STRING, required=False)
@lb.option("title", "title of the embed", hk.OptionType.STRING, required=False)
@lb.option("description", "description of the embed", hk.OptionType.STRING, required=False)
@lb.option("color", "color of the embed", hk.OptionType.STRING, required=False)
@lb.option("image", "image of the embed", hk.OptionType.ATTACHMENT, required=False)
@lb.option("imageurl", "image url of the embed", hk.OptionType.STRING, required=False)
@lb.option("thumbnail", "thumbnail of the embed", hk.OptionType.ATTACHMENT, required=False)
@lb.option("thumbnailurl", "thumbnail url of the embed", hk.OptionType.STRING, required=False)
@lb.option("authoricon", "author icon url", hk.OptionType.STRING, required=False)
@lb.option("authorurl", "author url", hk.OptionType.STRING, required=False)
@lb.option("authorname", "author name", hk.OptionType.STRING, required=False)
@lb.option("footericon", "author icon url", hk.OptionType.STRING, required=False)
@lb.option("footertext", "author name", hk.OptionType.STRING, required=False)
@lb.option("channel", "channel to send the embed", hk.OptionType.CHANNEL, required=False)
@lb.command("create", "create an embed", ephemeral=True)
@lb.implements(lb.SlashSubCommand)
async def create_embed(ctx: lb.SlashContext):
    thumbnail: hk.Attachment
    image: hk.Attachment
    channel: hk.GuildChannel

    embed = hk.Embed()
    embed_author = {"name": None, "icon": None, "url": None}
    embed_footer = {"text": None, "icon": None}
    content: str | None = None

    if url := ctx.options.url:
        embed.url = url

    if title := ctx.options.title:
        embed.title = title

    if description := ctx.options.description:
        embed.description = description

    if color := ctx.options.color:
        embed.color = color

    if image := ctx.options.image:
        image_bytes = await image.read()
        embed.set_image(image_bytes)

    if image_url := ctx.options.image_url:
        embed.set_image(hk.URL(image_url))

    if thumbnail := ctx.options.thumbnail:
        thumbnail_bytes = await thumbnail.read()
        embed.set_thumbnail(thumbnail_bytes)

    if thumbnail_url := ctx.options.thumbnail_url:

        embed.set_thumbnail(hk.URL(thumbnail_url))

    if msg_content := ctx.options.content:
        content = msg_content

    if authorname := ctx.options.authorname:
        embed_author["name"] = authorname

    if authoricon := ctx.options.authoricon:
        embed_author["icon"] = authoricon

    if authorurl := ctx.options.authorurl:
        embed_author["url"] = authorurl

    if footertext := ctx.options.footertext:
        embed_footer["text"] = footertext

    if footericon := ctx.options.footericon:
        embed_footer["icon"] = footericon

    embed.set_footer(**embed_footer)
    embed.set_author(**embed_author)

    try:

        channel = ctx.options.channel

        if channel is not None:

            if content is not None:
                await ctx.bot.rest.create_message(channel.id, content=content, embed=embed)

            else:
                await ctx.bot.rest.create_message(channel.id, embed=embed)

        else:
            if content is not None:
                await ctx.bot.rest.create_message(ctx.channel_id, content=content, embed=embed)

            else:
                await ctx.bot.rest.create_message(ctx.channel_id, embed=embed)

        await ctx.respond("done!")

    except hk.BadRequestError as e:
        await ctx.respond(e.message)

    except Exception as e:
        await ctx.respond(f"```{e}```")
