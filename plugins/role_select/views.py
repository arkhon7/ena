import typing

from lightbulb.utils.pag import EmbedPaginator
from lightbulb.utils.nav import ButtonNavigator

from .controller import ReactionRoleData


def create_roles_view(roles: typing.List[ReactionRoleData]):

    paginator = EmbedPaginator()
    for i, data in enumerate(roles):
        rra_id_str = f"{i+1}. <:{data.emoji_name}:{data.emoji_id}> :: <@&{data.role_id}> :: `rr_id: {data.id}`"
        paginator.add_line(rra_id_str)

    navigator = ButtonNavigator(paginator.build_pages())

    return navigator
