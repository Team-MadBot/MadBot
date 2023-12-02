import logging
import discord

from discord.ext import commands
from logging.handlers import RotatingFileHandler

class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def cog_load(self):
        logging.getLogger("discord").addHandler(RotatingFileHandler(
            filename="discord.log",
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,
            backupCount=10,
        ))
        self.logger = logging.getLogger("discord")
    
    def cog_unload(self):
        self.logger.removeHandler(self.logger.handlers[-1])
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.application_command: return
        assert interaction.command is not None
        logging.info(
            f"[SLASH USAGE] - '{interaction.user}' ({interaction.user.id}): '/{interaction.command.qualified_name}'"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
    print("Cog \"Logging\" запущен!")
