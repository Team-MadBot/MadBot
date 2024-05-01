from discord.ext import commands, tasks

from classes.bc_api import BoticordClient
from config import settings


class BoticordStatisticsCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bc_client: BoticordClient | None = None

    async def cog_load(self):
        self.bc_client = BoticordClient(settings["bcv2_token"])
        self.send_bot_stats.start()

    async def cog_unload(self):
        self.send_bot_stats.cancel()
        await self.bc_client.session.close()
        self.bc_client = None

    @tasks.loop(minutes=10)
    async def send_bot_stats(self):
        await self.bc_client.http.post_bot_stats(
            bot_id=self.bot.user.id,
            stats={
                "guilds": len(self.bot.guilds),
                "members": len(self.bot.users),
                "shards": len(self.bot.shards),
            },
        )

    @send_bot_stats.before_loop
    async def before_sending(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BoticordStatisticsCog(bot))
