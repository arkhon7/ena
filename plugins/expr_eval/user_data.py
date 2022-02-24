from __future__ import annotations

import re
import hikari
import lightbulb
import logging

from typing import List, Union
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
        self.add_field(name="Caller", value=f"```{self.macro.caller}```")
        self.add_field(name="Variables", value=f"```{self.var_str}```" if self.macro.variables else "None")
        self.add_field(name="Formula", value=f"```{self.macro.formula}```")
        self.add_field(name="Usage", value=f"```{self.usage}```")
        self.set_footer(text=f"{page}/{len(macros)}")


class UserDataPaginator(lightbulb.utils.EmbedPaginator):
    def __init__(
        self,
        max_chars: int = 400,
        prefix: str = "",
        suffix: str = "",
        line_separator: str = "\n\n",
    ) -> None:
        super().__init__(max_chars=max_chars, prefix=prefix, suffix=suffix, line_separator=line_separator)

    def paginate_macros(self, data: List[api.Macro]) -> UserDataPaginator:
        if data != []:
            for d in data:
                self.add_line(f"**{d.name}**\ncaller: {d.caller}")
            return self

        else:
            self.add_line("No macros saved!")
            return self

    def paginate_packages(self, data: List[api.MacroPackage]) -> UserDataPaginator:
        if data != []:
            for d in data:
                self.add_line(f"**{d.name}**\nprefix: {d.prefix}")
            return self

        else:
            self.add_line("No packages saved!")
            return self


# # utils
# def _get_curr_page(embed: hikari.Embed) -> Union[int, None]:
#     if embed.footer:
#         if embed.footer.text:
#             result = re.findall(r"([0-9]+)/[0-9]+", embed.footer.text)
#             if len(result) == 1:
#                 res = result[0]
#                 return res

#     return None
