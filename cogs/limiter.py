"""import discord
import logging

from discord.ext import commands

from config import *

logger = logging.getLogger('discord')

class Limiter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if len(self.bot.guilds) == 100 and not(self.bot.user.public_flags.verified_bot):
            guilds = sorted(self.bot.guilds, key = lambda x: x.member_count)
            for guild in guilds:
                if guild.member_count < settings['min_members'] and len(self.bot.guilds) > 90:
                    await guild.leave()

async def setup(bot: commands.Bot):
    await bot.add_cog(Limiter(bot))
"""