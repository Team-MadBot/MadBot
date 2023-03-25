import discord

from discord.ext import commands
from config import settings
from tools import models

class LaunchCog(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_connect(self):
        await self.bot.change_presence(
            activity=discord.Game(name="перезагрузка..."),
            status=discord.Status.idle
        )
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            activity=discord.Game(
                name="разработка v2"
            ),
            status=discord.Status.dnd
        )
        log_channel = self.bot.get_channel(settings["log_channel"])
        embed = discord.Embed(
            title="Бот перезагружен!",
            color=settings["color"],
            description=f"Средний пинг шардов: `{round(self.bot.latency * 1000)}ms`"
        )
        await log_channel.send(embed=embed)
        await self.bot.tree.sync()

async def setup(bot: models.MadBot):
    await bot.add_cog(LaunchCog(bot))