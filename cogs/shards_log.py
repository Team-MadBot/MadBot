import discord
import aiohttp
import logging

from discord.ext import commands
from config import settings

logger = logging.getLogger("discord")


class ShardLog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.WEBHOOK = settings["shard_log_hook_url"]

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id: int):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.WEBHOOK, session=session)
            embed = discord.Embed(
                title="Шард включился",
                color=discord.Color.yellow(),
                description=f"ID шарда: `{shard_id}`",
            )
            await webhook.send(embed=embed)
            await session.close()

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id: int):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.WEBHOOK, session=session)
            embed = discord.Embed(
                title="Шард отключился",
                color=discord.Color.yellow(),
                description=f"ID шарда: `{shard_id}`",
            )
            await webhook.send(embed=embed)
            await session.close()


"""
async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ShardLog(bot))
"""
