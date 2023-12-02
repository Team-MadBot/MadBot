import logging
import discord

from discord.ext import commands
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('discord')

class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.application_command: return
        assert interaction.command is not None
        logger.info(
            f"[SLASH USAGE] - '{interaction.user}' ({interaction.user.id}): '/{interaction.command.qualified_name}'"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
    logger.info("Cog \"Logging\" запущен!")
