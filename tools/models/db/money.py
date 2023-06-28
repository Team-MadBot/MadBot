from typing import Optional
from ..enums import GuildActionsType

class EditMoneyAction:
    def __init__(
        self, 
        _id: int, 
        guild_id: int, 
        user_id: int, 
        reason: Optional[str], 
        amount: int = 0
    ):
        self.id = _id
        self.guild_id = guild_id
        self.user_id = user_id
        self.amount = amount
        self.reason = reason

    def to_dict(self):
        dct = self.__dict__
        if dct.get('user_id') is not None:
            dct['user_id'] = str(dct['user_id'])
        if dct.get('guild_id') is not None:
            dct.pop('guild_id')
        return dct

class PatchMoneyAction(EditMoneyAction):
    def __init__(
        self, 
        guild_id: int, 
        user_id: int, 
        patcher_id: int, 
        reason: Optional[str], 
        amount: int
    ):
        self.patcher_id = patcher_id
        super().__init__(
            GuildActionsType.PATCH_MONEY, 
            guild_id, 
            user_id, 
            reason, 
            amount
        )
    
    def to_dict(self):
        dct = super().to_dict()
        dct['patcher_id'] = str(dct['patcher_id'])
        return dct

class TransferAction(EditMoneyAction):
    def __init__(
        self, 
        guild_id: int, 
        from_id: int, 
        to_id: int, 
        reason: Optional[str], 
        amount: int
    ):
        self.from_id = from_id
        self.to_id = to_id
        super().__init__(
            GuildActionsType.TRANSFER, 
            guild_id, 
            from_id, 
            reason, 
            amount
        )
        self.__delattr__("user_id")
    
    def to_dict(self):
        dct = super().to_dict()
        dct['from_id'] = str(dct['from_id'])
        dct['to_id'] = str(dct['to_id'])
        return dct

class BuyAction(EditMoneyAction):
    def __init__(
        self, 
        guild_id: int, 
        user_id: int, 
        item_id: int, 
        reason: Optional[str], 
        amount: int
    ):
        self.item_id = item_id
        super().__init__(
            GuildActionsType.BUY, 
            guild_id, 
            user_id, 
            reason, 
            amount
        )
