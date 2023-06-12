import discord
import config

from discord.ext import commands
from discord import app_commands
from checks import blacklist
from tools import models

class OnInteractionEvent(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    async def cog_load(self):
        self.__interaction_check = self.bot.tree.interaction_check
        self.bot.tree.interaction_check = self.interact_check
    
    async def cog_unload(self):
        self.bot.tree.interaction_check = self.__interaction_check

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            config.used_commands += 1
            config.last_command = '/' + interaction.command.qualified_name # type: ignore
    
    async def interact_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.id != 1080911312600694785 or not blacklist.in_blacklist(interaction): # type: ignore
            raise app_commands.CheckFailure("iznas")
        return True

async def setup(bot: models.MadBot):
    await bot.add_cog(OnInteractionEvent(bot))
