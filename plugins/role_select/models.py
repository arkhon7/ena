from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from ena.db import Base


class ReactionRoleAware(Base):
    __tablename__ = "reaction-role-aware"

    id = Column(String(32), primary_key=True)
    message_id = Column(String(21))
    channel_id = Column(String(21))
    guild_id = Column(String(21))

    children = relationship("ReactionRolePair")


class ReactionRole(Base):

    __tablename__ = "reaction-role"

    id = Column(String(32), primary_key=True)
    role_id = Column(String(21))
    emoji_id = Column(String(21))
    emoji_name = Column(String(50))
    animated = Column(Boolean)

    guild_id = Column(String(21))

    children = relationship("ReactionRolePair")


class ReactionRolePair(Base):
    __tablename__ = "reaction-role-pair"

    id = Column(String(32), primary_key=True)
    rr_id = Column(String(32), ForeignKey("reaction-role.id"))
    rr_aware_id = Column(String(32), ForeignKey("reaction-role-aware.id"))

    guild_id = Column(String(21))
