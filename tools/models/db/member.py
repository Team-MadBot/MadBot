from ..enums import GuildActionsType

class UserWarn:
    def __init__(
        self,
        guild_id: int,
        user_id: int,
        mod_id: int,
        until: int,
        reason: str
    ):
        self.id = GuildActionsType.WARN
        self.guild_id = guild_id
        self.user_id = user_id
        self.mod_id = mod_id
        self.until = until
        self.reason = reason
    
    def to_dict(self):
        dct = self.__dict__
        dct.pop("guild_id")
        dct['user_id'] = str(dct['user_id'])
        dct['mod_id'] = str(dct['mod_id'])
        return dct

class UserUnwarn(UserWarn):
    def __init__(self, 
        guild_id: int, 
        user_id: int, 
        mod_id: int, 
        reason: str
    ):
        super().__init__(
            guild_id, 
            user_id, 
            mod_id, 
            0, 
            reason
        )
        self.__delattr__("until")