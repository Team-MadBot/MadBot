from ..enums import GuildActionsType
from .abc import DBObjectBase
from dataclasses import dataclass, field
from typing import Final

@dataclass
class UserWarn(DBObjectBase):
    guild_id: int
    user_id: int
    mod_id: int
    until: int
    reason: str
    id: Final[int] = field(default=GuildActionsType.WARN, init=False)

@dataclass
class UserUnwarn(DBObjectBase):
    guild_id: int 
    user_id: int 
    mod_id: int 
    reason: str
    id: Final[int] = field(default=GuildActionsType.UNWARN, init=False)
