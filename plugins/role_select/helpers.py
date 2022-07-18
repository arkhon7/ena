import hashlib
import typing


T = typing.TypeVar("T")


def generate_reaction_role_aware_id(guild_id: str, channel_id: str, message_id: str) -> str:
    raw = guild_id + channel_id + message_id
    hash = hashlib.md5(raw.encode()).hexdigest()
    return hash


def generate_reaction_role_id(guild_id: str, emoji_id: str, emoji_name: str, role_id: str) -> str:
    raw = guild_id + emoji_id + emoji_name + role_id
    hash = hashlib.md5(raw.encode()).hexdigest()
    return hash


def generate_message_link(guild_id: str, channel_id: str, message_id: str):
    return f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"


def serialize(serializer: typing.Type[T], **kwargs) -> T:
    data = serializer(**kwargs)
    return data
