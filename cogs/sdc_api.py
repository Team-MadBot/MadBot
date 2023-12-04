import aiohttp
import logging

from discord.ext import commands, tasks
from config import settings

logger = logging.getLogger('discord')

class SDC_API(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.sdc_stats.start()

    def cog_unload(self):
        self.sdc_stats.cancel()

    @tasks.loop(seconds=1800.0)
    async def sdc_stats(self):
        headers = {
            'Authorization': settings['sdc_key']
        }
        body = {
            'servers': len(self.bot.guilds),
            'shards': len(self.bot.shards) 
        }

        assert self.bot.user is not None, "Bot user is None!"
        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                f"https://api.server-discord.com/v2/bots/{self.bot.user.id}/stats",
                headers=headers,
                data=body
            )
            if resp.ok:
                logger.info("Статистика на SDC обновлена!")
            else:
                data = await resp.read()
                logger.error("Статистика на SDC НЕ ОБНОВЛЕНА!:\n" + data.decode())
    
    @sdc_stats.before_loop
    async def before_stats_update(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(SDC_API(bot))
