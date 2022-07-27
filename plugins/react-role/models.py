from __future__ import annotations
from dataclasses import dataclass

import abc


def serialize(serializer: ReactionRolePluginModel, data: dict) -> ReactionRolePluginModel:
    return serializer.from_dict(data)


class ReactionRolePluginModel(abc.ABC):
    @abc.abstractmethod
    def from_dict(data: dict) -> ReactionRolePluginModel:
        raise NotImplementedError("Not implemented 'from_dict' method")


@dataclass
class ReactionRole(ReactionRolePluginModel):
    id: str
    role_id: int
    emoji_id: int
    emoji_name: str
    animated: bool
    guild_id: int

    @staticmethod
    def from_dict(data: dict):
        return ReactionRole(**data)


@dataclass
class ReactionRoleAware(ReactionRolePluginModel):
    id: str
    message_id: int
    channel_id: int
    guild_id: int

    @staticmethod
    def from_dict(data: dict):
        return ReactionRoleAware(**data)


@dataclass
class ReactionRolePair(ReactionRolePluginModel):
    id: str
    rr_id: str
    rr_aware_id: str
    guild_id: int

    @staticmethod
    def from_dict(data: dict):
        return ReactionRolePair(**data)
