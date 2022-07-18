from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from ena.db import Base


class ReactionRoleAware(Base):
    __tablename__ = "reaction-role-aware"

    id = Column(String(32), primary_key=True)
    message_id = Column(String(18))
    channel_id = Column(String(18))

    guild_id = Column(String(18))

    children = relationship("ReactionRoleConnection")


class ReactionRole(Base):

    __tablename__ = "reaction-role"

    id = Column(String(32), primary_key=True)
    role_id = Column(String(18))
    emoji_id = Column(String(18))
    emoji_name = Column(String(50))

    guild_id = Column(String(18))

    children = relationship("ReactionRoleConnection")


class ReactionRoleConnection(Base):
    __tablename__ = "reaction-role-connection"

    id = Column(String(32), primary_key=True)
    rr_id = Column(String(32), ForeignKey("reaction-role.id"))
    rrm_id = Column(String(32), ForeignKey("reaction-role-aware.id"))

    guild_id = Column(String(18))
