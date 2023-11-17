import aiohttp

from discord.ext import commands, tasks
from config import settings

class SDC_API(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.sdc_stats.start()

    def cog_unload(self):
        self.sdc_stats.cancel()

    @tasks.loop(seconds=300.0)
    async def sdc_stats(self):
        await self.bot.wait_until_ready()
        headers = {
            'Authorization': settings['sdc_key']
        }
        body = {
            'servers': len(self.bot.guilds),
            'shards': len(self.bot.shards) 
        }
        session = aiohttp.ClientSession()
        resp = await session.post(
            f"https://api.server-discord.com/v2/bots/{self.bot.user.id}/stats",
            headers=headers,
            data=body
        )
        if resp.ok:
            print("Статистика на SDC обновлена!")
        else:
            data = await resp.read()
            print(data)
        if not session.closed:
            await session.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(SDC_API(bot))
    print("Cog \"SDC API\" запущен!")
