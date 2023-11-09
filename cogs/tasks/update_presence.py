import discord

from discord.ext import commands
from discord.ext import tasks

class UpdatePresenceCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UpdatePresenceCog(bot))
