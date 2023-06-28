from typing import Optional, List, Literal

class GuildItem:
    """Guild item object.
    
    ID can be None if this is partial object (not created in DB)"""

    def __init__(
        self,
        id: int | None,
        guild_id: int,
        name: str,
        cost: int,
        description: str,
        req_role: Optional[int]
    ):
        self.id = id
        self.guild_id = guild_id
        self.name = name
        self.cost = cost
        self.description = description
        self.req_role = req_role
    
    @classmethod
    def from_dict(cls, guild_id: int, data: dict):
        self = cls.__new__(cls)

        self.id = data.get('id')
        self.guild_id = guild_id
        self.name = data['name']
        self.cost = data['cost']
        self.description = data['description']
        if data.get('req_role') is not None:
            self.req_role = int(data['req_role'])
        else:
            self.req_role = None

        return self

    def to_dict(self):
        dct: dict = self.__dict__
        dct.pop("guild_id")
        if self.req_role is None: dct['req_role'] = None
        else: dct['req_role'] = str(self.req_role)
        return dct

class GuildUser:
    def __init__(
        self,
        guild_id: int,
        user_id: int,
        balance: int,
        xp: int,
        level: int,
        inventory: List[GuildItem]
    ):
        self.guild_id = guild_id
        self.user_id = user_id
        self.balance = balance
        self.xp = xp
        self.level = level
        self.inventory = inventory

    @classmethod
    def from_dict(cls, data: dict, guild_id: int):
        self = cls.__new__(cls)
        self.guild_id = guild_id
        self.user_id = int(data['user_id'])
        self.balance = data['balance']
        self.xp = data['xp']
        self.level = data['level']
        self.inventory = [GuildItem.from_dict(guild_id, item) for item in data['inventory']]
        return self

class ButtonRole:
    def __init__(
        self,
        channel_id: int,
        message_id: int,
        type: Literal["single", "multiple"],
        roles: List[int]
    ):
        self.channel_id = channel_id
        self.message_id = message_id
        self.type = type
        self.roles = roles

    @classmethod
    def from_dict(cls, data: dict):
        self = cls.__new__(cls)
        self.channel_id = str(data['channel_id'])
        self.message_id = str(data['message_id'])
        self.type = data['type']
        self.roles = [int(role) for role in data['roles']]
        return self
    
    def to_dict(self):
        dct = self.__dict__
        dct["channel_id"] = str(dct['channel_id'])
        dct["message_id"] = str(dct['message_id'])
        dct["roles"] = [str(role) for role in dct["roles"]]

class BotGuild:
    def __init__(
        self,
        guild_id: int,
        members: List[GuildUser],
        items: List[GuildItem],
        autoroles: List[int],
        buttonroles: List[ButtonRole]
    ):
        self.guild_id = guild_id
        self.members = members
        self.items = items
        self.autoroles = autoroles
        self.buttonroles = buttonroles
