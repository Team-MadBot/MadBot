import discord

from discord.ext import commands

from classes import checks

class PingTrigger(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or checks.is_in_blacklist(message.author.id):
            return

        if message.content in [
            f"<@!{self.bot.user.id}>",
            f"<@{self.bot.user.id}>",
        ]:
            embed = discord.Embed(
                title="Привет! Рад, что я тебе чем-то нужен!", 
                color=discord.Color.orange(), 
                description="Бот работает на слеш-командах, поэтому для взаимодействия с ботом следует использовать их. Для большей информации пропишите `/help`."
            )
            await message.reply(embed=embed, mention_author=False)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(PingTrigger(bot))