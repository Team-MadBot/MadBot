import discord
import aiohttp
import logging

from discord.ext import commands

logger = logging.getLogger('discord')

class ShardLog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        # ОЙ БЛЯЯЯЯ
        self.WEBHOOK = "https://discord.com/api/webhooks/1096122874420547706/A764y4AlWYzy23zMTYt-yoYv8OewxNVpIogdTYcP27WqO1tNF1VuGKH34YSq7ef_6sAD"
    
    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id: int):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.WEBHOOK, session=session)
            embed = discord.Embed(
                title="Шард включился",
                color=discord.Color.yellow(),
                description=f"ID шарда: `{shard_id}`"
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
                description=f"ID шарда: `{shard_id}`"
            )
            await webhook.send(embed=embed)
            await session.close()
"""
async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ShardLog(bot))
    logger.info('Cog "ShardLog" запущен!')
"""
