from lightbulb.utils.pag import EmbedPaginator
from lightbulb.utils.nav import ButtonNavigator

from .helpers import generate_message_link
from .models import ReactionRoleAware
from .models import ReactionRolePair
from .models import ReactionRole


import typing as t


def create_reaction_role_pagination(rr_list: t.List[ReactionRole]):

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


def create_reaction_role_aware_pagination(rr_aware_list: t.List[ReactionRoleAware]):
    paginator = EmbedPaginator()
    for i, data in enumerate(rr_aware_list):

        rra_id_str = (
            f"{i+1}.`{data.id}` [link]({generate_message_link(data.guild_id, data.channel_id, data.message_id)})"
        )
        paginator.add_line(rra_id_str)

    navigator = ButtonNavigator(paginator.build_pages())

    return navigator


def create_reaction_role_pair_pagination(rr_pair_list: t.List[ReactionRolePair]):
    paginator = EmbedPaginator()
    for i, data in enumerate(rr_pair_list):
        if data.animated:
            _emoji = f"<a:{data.emoji_name}:{data.emoji_id}>"

        else:
            _emoji = f"<:{data.emoji_name}:{data.emoji_id}>"

        rra_id_str = (
            f"{i+1}. `{data.id}` {_emoji} :: <@&{data.role_id}> :: "
            f"[link]({generate_message_link(data.guild_id, data.channel_id, data.message_id)})"
        )
        paginator.add_line(rra_id_str)

    navigator = ButtonNavigator(paginator.build_pages())

    return navigator
