import logging
import config
import discord
import traceback

from boticordpy import BoticordClient
from .bc_websocket import BoticordWS
from discord.ext import commands
from config import settings, cogs

class MadBot(commands.AutoShardedBot):
    logger: logging.Logger
    boticordClient: BoticordClient

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
        self.log_level = logging.DEBUG if settings['debug_mode'] else logging.INFO
        assert settings["bc_token"]
        self.boticordClient = BoticordClient(settings['bc_token']) # type: ignore
    
    async def is_owner(self, user: discord.User):
        if user.id in config.coders:
            return True

        return await super().is_owner(user)
    
    async def setup_hook(self):
        self.logger.setLevel(self.log_level)
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
