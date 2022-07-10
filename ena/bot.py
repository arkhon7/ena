import miru
import hikari
import lightbulb

import os
import dotenv
import logging

from plugins import PLUGINS


dotenv.load_dotenv()
logging.basicConfig(level=logging.DEBUG)


class Ena(lightbulb.BotApp):
    def __init__(self):
        super().__init__(token=os.getenv("TOKEN"))
        miru.load(self)
        self.load_plugins(PLUGINS)
        # self.help_command = EnaHalp(self)

        # init
        self.subscribe(hikari.StartedEvent, self.on_start)

    def load_plugins(self, plugins: list):
        for plugin in plugins:
            try:
                self.load_extensions(f"plugins.{plugin}")
            except lightbulb.ExtensionMissingLoad:
                logging.debug(f"plugins/{plugin} is not a plugin, skipping...")

    # start event
    async def on_start(self, _: hikari.StartedEvent):

        await self.load_presence()

    # presence
    async def load_presence(self):

        await self.update_presence(
            status=hikari.Status.ONLINE,
            activity=hikari.Activity(
                name="/help",
                type=hikari.ActivityType.LISTENING,
            ),
        )


# class EnaHalp(lightbulb.BaseHelpCommand):
#     async def send_command_help(self, context: lightbulb.Context, command: lightbulb.Command) -> None:
#         if context.options.command == "calc":
#             paginated_help = lightbulb.utils.EmbedPaginator(max_chars=1000)

#             with open("tests/li.txt", "r") as sample:
#                 for line in sample.readlines():
#                     paginated_help.add_line(line)
#                 navigator = lightbulb.utils.ButtonNavigator(pages=paginated_help.build_pages())
#                 await navigator.run(context=context)
#             # await context.respond(content="help from calc")

#     async def send_bot_help(self, context):
#         # Override this method to change the message sent when the help command
#         # is run without any arguments.
#         ...

#     async def send_plugin_help(self, context, plugin):
#         # Override this method to change the message sent when the help command
#         # argument is the name of a plugin.
#         ...

#     async def send_group_help(self, context, group):
#         # Override this method to change the message sent when the help command
#         # argument is the name or alias of a command group.
#         ...

#     async def object_not_found(self, context, obj):
#         # Override this method to change the message sent when help is
#         # requested for an object that does not exist
#         ...
