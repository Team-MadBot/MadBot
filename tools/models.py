import discord
import config
import traceback

from typing import Optional, Literal
from discord.ext import commands
from config import settings, cogs
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
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(settings['prefix']),
            intents=settings['intents'],
            help_command=None,
            application_id=settings["bot_id"],
            shard_count=settings['shard_count']
        )
    
    async def is_owner(self, user: discord.User):
        if user.id in config.coders:
            return True

        return await super().is_owner(user)
    
    async def setup_hook(self):
        for ext in cogs:
            try:
                await self.load_extension(ext)
            except Exception as err:
                print(f"=============\nERROR WHILE LOADING COG {ext}!!!")
                traceback.print_exc()
                print("=============")
            else:
                print(f"Cog \"{ext}\" запущен!")

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

class GuildUser:
    def __init__(
        self,
        guild_id: int,
        user_id: int,
        balance: int,
        xp: int,
        level: int
    ):
        self.guild_id = guild_id
        self.user_id = user_id
        self.balance = balance
        self.xp = xp
        self.level = level

class EconomyActionIDs:    
    PATCH_MONEY = 1
    TRANSFER = 2
    BUY = 3

class EditMoneyAction:
    def __init__(self, _id: int, guild_id: int, user_id: int, reason: Optional[str], amount: int = 0):
        self.id = _id
        self.guild_id = guild_id
        self.user_id = user_id
        self.amount = amount
        self.reason = reason

    def to_dict(self):
        return self.__dict__

class PatchMoneyAction(EditMoneyAction):
    def __init__(self, guild_id: int, user_id: int, patcher_id: int, reason: Optional[str], amount: int):
        self.patcher_id = patcher_id
        super().__init__(1, guild_id, user_id, reason, amount)

class TransferAction(EditMoneyAction):
    def __init__(self, guild_id: int, user_id: int, transferrer_id: int, reason: Optional[str], amount: int):
        self.transferrer_id = transferrer_id
        super().__init__(2, guild_id, user_id, reason, amount)

class BuyAction(EditMoneyAction):
    def __init__(self, guild_id: int, user_id: int, item_id: int, reason: Optional[str], amount: int):
        self.item_id = item_id
        super().__init__(3, guild_id, user_id, reason, amount)
