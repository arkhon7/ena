from dataclasses import dataclass
import typing as t
import re
import hashlib

T = t.TypeVar("T")
DISCORD_MESSAGE_BASE_URL = "https://discord.com/channels"

NUMBER_REGEX = re.compile("([0-9]+)")


@dataclass
class DiscordMessage:
    id: int
    channel_id: int
    guild_id: int


def generate_hash(*args) -> str:
    raw = "".join([str(arg) for arg in args])
    hash = hashlib.md5(raw.encode()).hexdigest()

    return hash


def generate_message_link(guild_id: str, channel_id: str, message_id: str):
    return f"{DISCORD_MESSAGE_BASE_URL}/{guild_id}/{channel_id}/{message_id}"


def parse_message_from_link(message_link: str) -> DiscordMessage:
    ids = NUMBER_REGEX.findall(message_link)
    guild_id = int(ids[0])
    channel_id = int(ids[1])
    message_id = int(ids[2])

    return DiscordMessage(id=message_id, channel_id=channel_id, guild_id=guild_id)


def serialize(serializer: t.Type[T], **kwargs) -> T:
    data = serializer(**kwargs)
    return data
