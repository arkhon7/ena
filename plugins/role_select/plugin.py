import lightbulb
import hikari

role_select = lightbulb.Plugin("role-selection")


@role_select.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command(name="create_reaction_msg", description="create reaction message")
@lightbulb.implements(lightbulb.SlashCommand)
async def _create_reaction_message(ctx: lightbulb.Context):

    ROLES_CHANNEL_ID = 958156380559257660

    banner_embed = hikari.Embed(color="#36393f")
    banner_embed.set_image(hikari.URL("https://c.tenor.com/ACxZLKSQf8IAAAAC/ena-shinonome-ena.gif"))

    intro_embed = hikari.Embed(
        title=("**```            Role Selection           ```**"),
        description=(
            "Check out the roles that we have provided for you to have a customized feel on this server!\n\n"
            "**Disclaimer**: Each of the roles provided will unlock a certain category which will have another "
            "**roles (TODO)** channel for specifiying channels you want to see.\n"
        ),
        color="#36393f",
    )
    intro_embed.set_image(
        hikari.URL("https://cdn.discordapp.com/attachments/857365300966326292/879858842224185404/white2.png")
    )

    reaction_embed = hikari.Embed(
        title=("**```          Choose A Category         ```**"),
        description=(
            "<a:pink_verified_icon:995312808780644423> :: <@&995335085698076732>\n"
            "<a:purple_verified_icon:995312789419728916> :: <@&995564101902278736>\n"
            "<a:blue_verified_icon:995312743185911808> :: <@&995335036490498198>\n"
            "<a:orange_verified_icon:995337599067627570> :: <@&995335303927697510>\n"
            "<a:green_verified_icon:995312690522226708> :: <@&995338406139793408>\n"
        ),
        color="#36393f",
    )
    reaction_embed.set_image(
        hikari.URL("https://cdn.discordapp.com/attachments/857365300966326292/879858842224185404/white2.png")
    )

    await ctx.bot.rest.create_message(channel=ROLES_CHANNEL_ID, embed=banner_embed)
    await ctx.bot.rest.create_message(channel=ROLES_CHANNEL_ID, embed=intro_embed)
    reaction_message = await ctx.bot.rest.create_message(channel=ROLES_CHANNEL_ID, embed=reaction_embed)

    await reaction_message.add_reaction(emoji="pink_verified_icon", emoji_id=995312808780644423)
    await reaction_message.add_reaction(emoji="purple_verified_icon", emoji_id=995312789419728916)
    await reaction_message.add_reaction(emoji="blue_verified_icon", emoji_id=995312743185911808)
    await reaction_message.add_reaction(emoji="orange_verified_icon", emoji_id=995337599067627570)
    await reaction_message.add_reaction(emoji="green_verified_icon", emoji_id=995312690522226708)

    await ctx.respond("done creating the reaction message!")


@role_select.listener(hikari.ReactionAddEvent)  # type: ignore
async def handle_reaction_add(event: hikari.ReactionAddEvent):

    reaction_role_handler = role_select.bot.d["reaction_role_handler"]
    await reaction_role_handler.add_role_to_member(event.emoji_name, event.user_id)


@role_select.listener(hikari.ReactionDeleteEvent)  # type: ignore
async def handle_reaction_remove(event: hikari.ReactionDeleteEvent):

    reaction_role_handler = role_select.bot.d["reaction_role_handler"]
    await reaction_role_handler.remove_role_from_member(event.emoji_name, event.user_id)
