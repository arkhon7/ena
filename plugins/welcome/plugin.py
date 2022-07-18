import hikari
import lightbulb


plugin = lightbulb.Plugin("welcome-plugin")


@plugin.listener(hikari.MemberCreateEvent)
async def handle_member_join(event: hikari.MemberCreateEvent):
    print(event)


@plugin.listener(hikari.MemberDeleteEvent)
async def handle_member_leave(event: hikari.MemberDeleteEvent):
    print(event)
