import discord

from discord.ext import commands
from tools import models

class GetNewMembersWithoutIntentsCog(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.type == discord.MessageType.new_member:
            await message.channel.send(f"{message.author.mention} зашёл на сервер!")

async def setup(bot: models.MadBot):
    await bot.add_cog(GetNewMembersWithoutIntentsCog(bot))
