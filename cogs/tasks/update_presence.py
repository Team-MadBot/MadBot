import discord

from discord.ext import commands
from discord.ext import tasks
from contextlib import suppress

class UpdatePresenceCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    async def cog_load(self):
        self.update_presence.start()

    async def cog_unload(self):
        self.update_presence.cancel()

    @tasks.loop(seconds=60)
    async def update_presence(self):
        guilds_count = len(self.bot.guilds)
        rounded_count = round(guilds_count / 1000, 1)
        irounded_count = round(guilds_count / 1000)
        for shard in range(len(self.bot.shards)):
            with suppress(Exception):
                await self.bot.change_presence(
                    activity=discord.CustomActivity(
                        name=f"Шард {shard} | "
                        f"{rounded_count if irounded_count != rounded_count else irounded_count}k серверов"
                    ),
                    status=discord.Status.dnd, 
                    shard_id=shard
                )
    
    @update_presence.before_loop
    async def before_update_presence(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UpdatePresenceCog(bot))
