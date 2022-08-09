from dataclasses import dataclass
import typing as t


@dataclass
class EmojiRolePair:

    id: str
    role_id: int
    emoji_id: int
    emoji_name: str
    is_animated: bool
    guild_id: int

    @staticmethod
    def from_dict(data: t.Dict):
        return EmojiRolePair(**data)


@dataclass
class ActiveEmojiRolePair:

    id: str
    role_id: int
    emoji_id: int
    emoji_name: str
    is_animated: bool
    message_id: int
    channel_id: int
    guild_id: int

    @staticmethod
    def from_dict(data: t.Dict):
        return ActiveEmojiRolePair(**data)


# CACHE


@dataclass
class EmojiRolePairCache:

    ids: t.Dict[str, str]
    by_guild: t.List[t.Any]
    by_message: t.Dict[int, t.List[t.Any]]
    by_channel: t.Dict[int, t.List[t.Any]]
