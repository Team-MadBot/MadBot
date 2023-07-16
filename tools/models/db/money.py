from typing import Optional, ClassVar
from ..enums import GuildActionsType
from dataclasses import dataclass, field
from .guild import GuildAction

@dataclass
class EditMoneyAction(GuildAction):
    id: ClassVar[int]
    guild_id: int
    user_id: int
    reason: Optional[str]
    amount: int

@dataclass
class PatchMoneyAction(EditMoneyAction):
    patcher_id: int
    id: ClassVar[int] = field(default=GuildActionsType.PATCH_MONEY, init=False)

@dataclass
class TransferAction(PatchMoneyAction):
    """Dataclass of money transfer action.
    
    patcher_id - user that sent bucks
    user_id - user that got bucks"""
    id: ClassVar[int] = field(default=GuildActionsType.TRANSFER, init=False)

@dataclass
class BuyAction(EditMoneyAction):
    item_id: int
    id: ClassVar[int] = field(default=GuildActionsType.BUY, init=False)
