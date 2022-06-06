import discord
from discord.ext import commands

class Limiter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if len(self.bot.guilds) == 100 and not(self.bot.user.public_flags.verified_bot):
            for guild in self.bot.guilds:
                if guild.member_count < 5 and len(self.bot.guilds) > 90:
                    await guild.leave()

async def setup(bot: commands.Bot):
    await bot.add_cog(Limiter(bot))
    print("Cog \"Limiter\" запущен!")