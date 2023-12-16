import discord

from discord.ext import commands
from classes import db

class OnInteractionCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            assert interaction.command is not None
            await db.update_used_commands()
            await db.update_last_command('/' + interaction.command.qualified_name)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(OnInteractionCog(bot))