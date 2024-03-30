import time

from discord.ext import commands
from discord.ext import tasks

from classes import db

class CheckBlacklistCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    async def cog_load(self):
        self.check_blacklist.start()

    async def cog_unload(self):
        self.check_blacklist.cancel()

    @tasks.loop(seconds=1)
    async def check_blacklist(self):  # fucking scary
        async for resource in db.get_all_blacklist():
            if resource['until'] < int(time.time()):
                await db.remove_blacklist(resource['resource_id'])

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(CheckBlacklistCog(bot))
