import logging
import time
from contextlib import suppress

import discord
from discord.ext import commands, tasks

from classes import db

logger = logging.getLogger('discord')

class UpdateStatsCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    async def cog_load(self):
        self.update_stats.start()

    async def cog_unload(self):
        self.update_stats.cancel()
    
    @tasks.loop(seconds=1)
    async def update_stats(self):
        async for guild in db.get_guilds_stats():
            if guild['next_update'] > time.time(): continue
            for channel_id in guild['channels']:
                with suppress(Exception):
                    channel = self.bot.get_channel(int(channel_id['id']))
                    assert isinstance(channel, discord.abc.GuildChannel)
                    discord_guild = channel.guild
                    assert discord_guild.member_count is not None

                    if channel is None: continue
                    stat = self.get_stat(channel_id['type'], discord_guild)
                    try:
                        await channel.edit(name=channel_id['text'].replace('%count%', str(stat)))
                    except Exception as e:
                        if not isinstance(e, discord.Forbidden):
                            logger.error(e)
            await db.update_guild_stats(
                guild_id=guild['id'],
                next_update=int(time.time()) + 600
            )
    
    def get_stat(self, channel_type: str, guild: discord.Guild):
        assert guild.member_count is not None
        match channel_type:
            case 'online':
                return len(list(filter(lambda x: x.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd], guild.members)))
            case 'members':
                return guild.member_count
            case 'people':
                return guild.member_count - len(list(filter(lambda x: x.bot, guild.members)))
            case 'bots':
                return len(list(filter(lambda x: x.bot, guild.members)))
            case 'emojis':
                return len(guild.emojis)
            case 'voice':
                return sum(len(c.voice_states) for c in guild.voice_channels)
    
    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UpdateStatsCog(bot))
