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
        self.bot.logger.info("Connecting to Gateway...")
    
    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id: int):
        await self.bot.change_presence(
            activity=discord.Game(
                name=f"разработка v2 | Шард {shard_id}"
            ),
            status=discord.Status.dnd,
            shard_id=shard_id
        )
        log_channel = self.bot.get_channel(settings["log_channel"])
        embed = discord.Embed(
            title=f"Шард {shard_id} перезагружен!",
            color=settings["color"],
            description=f"Пинг шарда: `{round(self.bot.get_shard(shard_id).latency * 1000)}ms`" # type: ignore
        )
        await log_channel.send(embed=embed) # type: ignore
        self.bot.logger.info(f"Shard ID {shard_id} is ready!")

async def setup(bot: models.MadBot):
    await bot.add_cog(LaunchCog(bot))