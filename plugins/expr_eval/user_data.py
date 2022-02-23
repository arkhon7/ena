import re
import hikari
import miru
import logging

from typing import AnyStr, Dict, List, Union, Optional
from plugins.expr_eval import api


logging = logging.getLogger(__name__)  # type: ignore


class UserMacrosEmbed(hikari.Embed):
    def __init__(self, macros: List[api.Macro], page=1) -> None:
        super().__init__()
        self.macro = macros[page - 1]
        self.var_str = ", ".join([var for var in self.macro.variables]) if self.macro.variables else ""
        self.usage = f"{self.macro.caller}({self.var_str})"
        self.title = self.macro.name
        self.description = self.macro.description if self.macro.description else "No description"
        self.add_field(name="Caller", value=self.macro.caller)
        self.add_field(name="Variables", value=self.var_str if self.macro.variables else "None")
        self.add_field(name="Formula", value=self.macro.formula)
        self.add_field(name="Usage", value=self.usage)
        self.set_footer(text=f"{page}/{len(macros)}")


class UserMacroView(miru.View):
    def __init__(self, expr_handler: api.EnaExpr) -> None:
        super().__init__()
        self.expr_handler = expr_handler

    @miru.button(label="<<", custom_id="first-macro-btn", style=hikari.ButtonStyle.PRIMARY)
    async def __first_macro(self, button: miru.Button, context: miru.Context):
        ...

    @miru.button(label="<", custom_id="next-macro-btn", style=hikari.ButtonStyle.PRIMARY)
    async def __next_macro(self, button: miru.Button, context: miru.Context):
        ...

    @miru.button(label=">", custom_id="back-macro-btn", style=hikari.ButtonStyle.PRIMARY)
    async def __back_macro(self, button: miru.Button, context: miru.Context):
        ...

    @miru.button(label=">>", custom_id="last-macro-btn", style=hikari.ButtonStyle.PRIMARY)
    async def __last_macro(self, button: miru.Button, context: miru.Context):
        ...


class UserMacroSelect(miru.Select):
    def __init__(self, macros: List[api.Macro]) -> None:
        super().__init__()
        self.options = []


# utils
def _get_curr_page(embed: hikari.Embed) -> Union[int, None]:
    if embed.footer:
        if embed.footer.text:
            result = re.findall(r"([0-9]+)/[0-9]+", embed.footer.text)
            if len(result) == 1:
                res = result[0]
                return res

    return None
