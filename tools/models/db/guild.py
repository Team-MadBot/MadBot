from typing import Optional, List, Literal
from dataclasses import dataclass
from .abc import DBObjectBase

@dataclass
class GuildAction(DBObjectBase):
    """Guild action object.
    
    It's a global class for guild actions."""

@dataclass
class GuildItem(DBObjectBase):
    """Guild item object.
    
    ID can be None if this is partial object (not created in DB)"""
    id: int
    guild_id: int
    name: str
    cost: int
    description: str
    req_role_id: int

@dataclass
class GuildUser(DBObjectBase):
    guild_id: int
    user_id: int
    balance: int
    xp: int
    level: int
    inventory: List[GuildItem]

@dataclass
class ButtonRole(DBObjectBase):
    channel_id: int
    message_id: int
    type: Literal["single", "multiple"]
    roles: List[int]

@dataclass
class BotGuild(DBObjectBase):
    guild_id: int
    members: List[GuildUser]
    items: List[GuildItem]
    autoroles: List[int]
    buttonroles: List[ButtonRole]
