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
    ADD_MONEY = 1
    REMOVE_MONEY = 2
    TRANSFER = 3
    BUY = 4
    API_PATCH = 5

class EditMoneyAction:
    def __init__(self, _id: int, user_id: int, amount: int = 0):
        self.id = _id
        self.user_id = user_id
        self.amount = amount

    def to_dict(self, reason: Optional[str]):
        return self.__dict__.update({'reason': reason})

class PatchMoneyAction(EditMoneyAction):
    def __init__(self, _id: int, user_id: int, patcher_id: int, reason: Optional[str], amount: int):
        self.patcher_id = patcher_id
        self.reason = reason
        super().__init__(_id, user_id, amount)

class TransferAction(EditMoneyAction):
    def __init__(self, _id: int, user_id: int, transferrer_id: int, reason: Optional[str], amount: int):
        self.transferrer_id = transferrer_id
        self.reason = reason
        super().__init__(_id, user_id, amount)

class BuyAction(EditMoneyAction):
    def __init__(self, _id: int, user_id: int, item_id: int, amount: int):
        self.item_id = item_id
        super().__init__(_id, user_id, amount)
