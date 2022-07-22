import typing

from lightbulb.utils.pag import EmbedPaginator
from lightbulb.utils.nav import ButtonNavigator

from .helpers import generate_message_link

from .controller import ReactionRoleAwareData
from .controller import ReactionRoleData


def create_rr_pagination(rr_list: typing.List[ReactionRoleData]):

    paginator = EmbedPaginator()
    for i, data in enumerate(rr_list):

        if data.animated:
            _emoji = f"<a:{data.emoji_name}:{data.emoji_id}>"

        else:
            _emoji = f"<:{data.emoji_name}:{data.emoji_id}>"

        rr_data_str = f"{i+1}. {_emoji} :: <@&{data.role_id}> :: `rr_id: {data.id}`"
        paginator.add_line(rr_data_str)

    navigator = ButtonNavigator(paginator.build_pages())

    return navigator


def create_rr_aware_pagination(rr_aware_list: typing.List[ReactionRoleAwareData]):
    paginator = EmbedPaginator()
    for i, data in enumerate(rr_aware_list):

        rra_id_str = (
            f"{i+1}.`{data.id}` [link]({generate_message_link(data.guild_id, data.channel_id, data.message_id)})"
        )
        paginator.add_line(rra_id_str)

    navigator = ButtonNavigator(paginator.build_pages())

    return navigator
