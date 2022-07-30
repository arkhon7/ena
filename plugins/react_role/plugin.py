import lightbulb as lb

from .pairs import _create_pair
from .pairs import _delete_pair
from .pairs import _info_pair
from .pairs import _all_pairs

plugin = lb.Plugin("reaction-role-plugin", include_datastore=True)


@plugin.command
@lb.command("react_role", "reactrole command group")
@lb.implements(lb.SlashCommandGroup)
async def _react_role():
    pass


# emoji role pair commands
_react_role.child(_create_pair)
_react_role.child(_delete_pair)
_react_role.child(_info_pair)
_react_role.child(_all_pairs)
