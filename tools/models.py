import discord
import config
import logging
import traceback

from typing import (
    Optional, 
    Literal,
    List
)
from discord.ext import commands
from config import settings, cogs
from enum import IntEnum
# from tools import db

NC_CATEGORIES = Literal[
    'baka', 
    'cry', 
    'cuddle', 
    'happy', 
    'hug', 
    'kiss', 
    'sad', 
    'wag', 
    'poke', 
    'pat', 
    'dance', 
    'smug', 
    'wave', 
    'menhera-chan'
]
SDC_URL = "https://api.server-discord.com/v2/bots/{bot_id}/stats"

class MadBot(commands.AutoShardedBot):
    logger: logging.Logger

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(settings['prefix']), # type: ignore
            intents=settings['intents'],
            help_command=None,
            application_id=settings["bot_id"],
            shard_count=settings['shard_count']
        )
        logger = logging.getLogger("discord.ext.commands.bot")
        logger.name = "MadBot"
        self.logger = logger
    
    async def is_owner(self, user: discord.User):
        if user.id in config.coders:
            return True

        return await super().is_owner(user)
    
    async def setup_hook(self):
        for ext in cogs:
            try:
                await self.load_extension(ext)
            except Exception as err:
                self.logger.error(
                    f"Error has occured while loading {ext} cog:\n"
                    f"{traceback.format_exc()}\n"
                    f"==========================================="
                )
            else:
                self.logger.info(f"Cog \"{ext}\" loaded!")

class BlackList:
    def __init__(
            self, 
            user_id: int, 
            blocked_at: int,
            reason: Optional[str],
            blocked_until: Optional[int]
        ):
        self.user_id = user_id
        self.reason = reason
        self.blocked_at = blocked_at
        self.blocked_until = blocked_until
    
    # def unblock(self) -> bool:
    #     return db.remove_blacklist(self.user_id)

class GuildItem:
    def __init__(
        self,
        id: int,
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

        self.id = data['id']
        self.guild_id = guild_id
        self.name = data['name']
        self.cost = data['cost']
        self.description = data['description']
        if data.get('req_role') is not None:
            self.req_role = int(data['req_role'])
        else:
            self.req_role = None

        return self

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

class GuildActionsType(IntEnum):    
    PATCH_MONEY = 1
    TRANSFER = 2
    BUY = 3
    WARN = 4
    UNWARN = 5

class EditMoneyAction:
    def __init__(self, _id: int, guild_id: int, user_id: int, reason: Optional[str], amount: int = 0):
        self.id = _id
        self.guild_id = guild_id
        self.user_id = user_id
        self.amount = amount
        self.reason = reason

    def to_dict(self):
        dct = self.__dict__
        dct['user_id'] = str(dct['user_id'])
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

class TransferAction(EditMoneyAction):
    def __init__(
        self, 
        guild_id: int, 
        from_id: int, 
        to_id: int, 
        reason: Optional[str], 
        amount: int
    ):
        super().__init__(
            GuildActionsType.TRANSFER, 
            guild_id, 
            from_id, 
            reason, 
            amount
        )
        self.__delattr__("user_id")
        self.from_id = from_id
        self.to_id = to_id

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
