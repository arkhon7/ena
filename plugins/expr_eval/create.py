import hikari
import miru
import logging

from typing import Dict, Optional
from plugins.expr_eval import api

logging = logging.getLogger(__name__)  # type: ignore
expr_eval = api.EnaExpr()


class CreateMacroForm(miru.Modal):
    """A modal/form for getting macro data inputs."""

    """
    name: str
    owner_id: str
    description: str
    caller: str
    formula: str
    variables: Optional[List[str]] = None
    """

    def __init__(self, values: Optional[Dict[str, str]] = None) -> None:
        super().__init__(title="Create a Macro", custom_id="create-macro-form")

        self.add_item(
            miru.TextInput(
                custom_id="name",
                label="Name",
                placeholder="e.g. A cool macro that I use",
                min_length=2,
                max_length=100,
                required=True,
                value=values["name"] if values else None,
            )
        )
        self.add_item(
            miru.TextInput(
                custom_id="description",
                label="Description (Optional)",
                placeholder="e.g. This is a reaally cool macro",
                max_length=2000,
                style=hikari.TextInputStyle.PARAGRAPH,
                value=values["description"] if values else None,
            )
        )
        self.add_item(
            miru.TextInput(
                custom_id="caller",
                label="Caller",
                placeholder="e.g. coolMacro",
                max_length=30,
                required=True,
                value=values["caller"] if values else None,
            )
        )
        self.add_item(
            miru.TextInput(
                custom_id="variables",
                label="Variables (Optional)",
                placeholder="e.g. var1 | Use commas if using multiple variables.",
                value=values["variables"] if values else None,
            )
        )
        self.add_item(
            miru.TextInput(
                custom_id="formula",
                label="Formula",
                placeholder="e.g. {var1} + {var2} | Enclose variables inside the braces.",
                required=True,
                style=hikari.TextInputStyle.PARAGRAPH,
                value=values["formula"] if values else None,
            )
        )

    async def callback(self, context: miru.ModalContext) -> None:
        logging.debug("WORKING SUBMIT MODAL")

        values = dict()
        if context.values:
            for k, v in context.values.items():
                if k.custom_id:
                    values[k.custom_id] = v

        confirmation_embed = MacroConfirmationEmbed(values)
        confirmation_view = MacroConfirmationView()

        await context.respond(embed=confirmation_embed, components=confirmation_view.build())
        message = await context.fetch_response()
        confirmation_view.start(message)


class MacroConfirmationEmbed(hikari.Embed):
    def __init__(self, values: Dict[str, str]) -> None:
        super().__init__()
        self.title = "Macro Confirmation"
        self.description = "Please check carefully the details below."

        for custom_id, value in values.items():
            self.add_field(name=custom_id.capitalize(), value=f"```\n{value}\n```")


class MacroConfirmationView(miru.View):
    def __init__(self) -> None:
        super().__init__()

    @miru.button(label="Submit", custom_id="submit-macro-form-btn")
    async def _submit_macro(self, button: miru.Button, context: miru.Context):
        await context.defer()
        interaction: miru.ComponentInteraction = context.interaction
        message: hikari.Message = interaction.message
        embed: hikari.Embed = message.embeds[0]
        user_id: str = str(context.user.id)
        fields = embed.fields

        name: hikari.EmbedField = fields[0]
        desc: hikari.EmbedField = fields[1]
        call: hikari.EmbedField = fields[2]
        vars: hikari.EmbedField = fields[3]
        frml: hikari.EmbedField = fields[4]

        macro_data = {
            "name": name.value[3:-3].strip(),
            "owner_id": user_id,
            "description": desc.value[3:-3].strip(),
            "caller": call.value[3:-3].strip(),
            "variables": vars.value[3:-3].strip().split(","),
            "formula": frml.value[3:-3].strip(),
        }

        resp = await expr_eval.create_macro(macro_data=macro_data)

        if resp.error:
            await context.respond(content=resp.error.message)

        else:
            await context.respond(content=resp.message)

    @miru.button(label="Edit", custom_id="edit-macro-form-btn")
    async def _edit_macro(self, button: miru.Button, context: miru.ViewContext):
        interaction: miru.ComponentInteraction = context.interaction
        message: hikari.Message = interaction.message
        embed: hikari.Embed = message.embeds[0]

        macro_data = {field.name.lower(): field.value[3:-3].strip() for field in embed.fields}
        # embed_to_edit: hikari.Embed = interaction.message.embeds[0]

        logging.debug(macro_data)
        modal = CreateMacroForm(values=macro_data)
        await context.respond_with_modal(modal)


# class LoaderEmbed(hikari.Embed):
#     def __init__(self) -> None:
#         super().__init__()
#         self.set_image(
#             hikari.URL(
#                 "https://cdn.discordapp.com/attachments/886112309020348466/904663908072161280/Magnify-1s-207px.gif"
#             )
#         )
