from dataclasses import dataclass
import hashlib
import typing
import re


T = typing.TypeVar("T")
DISCORD_MESSAGE_BASE_URL = "https://discord.com/channels"

NUMBER_REGEX = re.compile("([0-9]+)")


@dataclass
class DiscordMessage:
    id: str
    channel_id: str
    guild_id: str


def generate_hash(*args) -> str:

    raw = "".join([arg for arg in args])
    hash = hashlib.md5(raw.encode()).hexdigest()
    return hash


def generate_message_link(guild_id: str, channel_id: str, message_id: str):
    return f"{DISCORD_MESSAGE_BASE_URL}/{guild_id}/{channel_id}/{message_id}"


def parse_message_from_link(message_link: str):
    ids = NUMBER_REGEX.findall(message_link)
    guild_id = ids[0]
    channel_id = ids[1]
    message_id = ids[2]

    return DiscordMessage(id=message_id, channel_id=channel_id, guild_id=guild_id)


def serialize(serializer: typing.Type[T], **kwargs) -> T:
    data = serializer(**kwargs)
    return data


# def serialize_many(serializer: typing.Type[T], datalist: list[dict]) -> list[T]:

#     return [serialize(serializer, **d) for d in datalist]


# def add(a, b):
#     return sum()


# print(serialize(add, (1, 2)))
