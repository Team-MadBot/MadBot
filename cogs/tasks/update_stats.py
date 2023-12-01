import discord
import time

from discord.ext import commands
from discord.ext import tasks

from config import client

class UpdateStatsCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @tasks.loop(seconds=30)
    async def update_stats(self):
        db = client.stats # TODO
        coll = db.guilds
        guilds = coll.find()
        for guild in guilds:
            if guild['next_update'] > time.time(): continue
            for channel_id in guild['channels']:
                channel = self.bot.get_channel(int(channel_id['id']))
                assert isinstance(channel, discord.abc.GuildChannel)
                discord_guild = channel.guild
                assert discord_guild.member_count is not None

                if channel is None: continue
                stat = self.get_stat(channel_id['type'], discord_guild)
                try:
                    await channel.edit(name=channel_id['text'].replace('%count%', str(stat)))
                except Exception as e:
                    print(e)
            coll.update_one({'id': guild['id']}, {'$set': {'next_update': round(time.time()) + 600}})
    
    def get_stat(self, channel_type: str, guild: discord.Guild):
        assert guild.member_count is not None
        match channel_type:
            case 'online':
                return len(list(filter(lambda x: x.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd], guild.members)))
            case 'members':
                return guild.member_count
            case 'people':
                guild.max_members
                return guild.member_count - len(list(filter(lambda x: x.bot, guild.members)))
            case 'bots':
                return len(list(filter(lambda x: x.bot, guild.members)))
            case 'emojis':
                return len(guild.emojis)
            case 'voice':
                return len(guild.voice_channels)
    
    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UpdateStatsCog(bot))
