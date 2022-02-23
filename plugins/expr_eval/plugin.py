import lightbulb
import hikari
import logging

from plugins.expr_eval.api import EnaExpr
from plugins.expr_eval.create import CreateMacroForm

expr_eval_plugin = lightbulb.Plugin("Expression Evaluator plugin")
logging = logging.getLogger(__name__)  # type: ignore
expr_eval = EnaExpr()


TEST_GUILDS = [938346141723033600, 938374580244979764, 880968014500069506, 806168806166364170]


@expr_eval_plugin.command
@lightbulb.option(name="expr", description="expression to calculate")
@lightbulb.command(name="calc", description="calculate math here!", guilds=TEST_GUILDS)
@lightbulb.implements(lightbulb.SlashCommand)
async def _calc(context: lightbulb.Context):
    # create loader here

    user_id: str = str(context.user.id)
    if expr := context.options.expr:
        resp = await expr_eval.calculate(expr, user_id)
        await context.respond("Input:\n" "```py\n" f"{expr}" "```" "Result:\n" "```py\n" f"{resp.data}" "```")


@expr_eval_plugin.command
@lightbulb.option(
    name="command",
    description="the name of command you're confused on",
    required=False,
    choices=[
        hikari.CommandChoice(name="calc", value="calc"),
        hikari.CommandChoice(name="create", value="create"),
    ],
)
@lightbulb.command(name="help", description="need my help?", guilds=TEST_GUILDS)
@lightbulb.implements(lightbulb.SlashCommand)
async def _help(context: lightbulb.SlashContext):
    logging.debug(" Help command called!")

    if help_class := context.bot.help_command:
        logging.debug(f" Found help command class {help_class}")
        if context.options.command == "calc":
            command: lightbulb.SlashCommand = context.command
            await help_class.send_command_help(context=context, command=command)


# CREATION COMMANDS


@expr_eval_plugin.command
@lightbulb.command(name="create", description="creation commands", guilds=TEST_GUILDS)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _create(context: lightbulb.Context):
    """CREATION COMMANDS GROUP"""
    pass


@_create.child
@lightbulb.command(
    name="macro",
    description="create a macro!",
    guilds=TEST_GUILDS,
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _create_macro(context: lightbulb.Context):

    modal = CreateMacroForm()
    if context.interaction:
        await modal.send(interaction=context.interaction)


# @_create.child
# @lightbulb.command(
#     name="package",
#     description="create a package!",
#     guilds=TEST_GUILDS,
# )
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def _create_package(context: lightbulb.Context):
#     pass


# USER DATA COMMANDS
@expr_eval_plugin.command
@lightbulb.command(name="my", description="your saved data", guilds=TEST_GUILDS)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _my(context: lightbulb.Context):
    """USER DATA COMMANDS GROUP"""
    pass


@_my.child
@lightbulb.command(
    name="macros",
    description="get your macros!",
    guilds=TEST_GUILDS,
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _my_macros(context: lightbulb.Context):
    user_id: str = str(context.user.id)
    user_macros = await expr_eval.fetch_macros(user_id=user_id)
    print(user_macros)


@_my.child
@lightbulb.command(
    name="environment",
    description="get your evaluation environment!",
    guilds=TEST_GUILDS,
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _my_environment(context: lightbulb.Context):
    user_id: str = str(context.user.id)
    user_environment = await expr_eval.fetch_environment(user_id=user_id)
    print(user_environment)


@_my.child
@lightbulb.command(
    name="packages",
    description="get your packages!",
    guilds=TEST_GUILDS,
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _my_packages(context: lightbulb.Context):
    user_id: str = str(context.user.id)
    user_packages = await expr_eval.fetch_packages(user_id=user_id)
    print(user_packages)
