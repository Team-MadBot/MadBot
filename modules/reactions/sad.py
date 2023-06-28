import discord

from discord.ext import commands
from discord import app_commands
from tools.models import MadBot
from pynepcord.errors import NepuError
from tools.api import Requests

class Sad(commands.Cog):
    def __init__(self, bot: MadBot):
        self.bot = bot
    
    @app_commands.command(name="sad", description="Реакция грусти")
    async def sad_react(self, interaction: discord.Interaction):
        requests = Requests()
        try:
            img_url = await requests.nc_get_image("sad")
        except NepuError as e:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Стороннее API сейчас недоступно. Попробуйте позже."
            ).set_image(url="https://http.cat/500")
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Реакция - Грусть",
                color=discord.Color.orange(),
                description=f"{interaction.user.mention} грустит."
            ).set_image(url=img_url)
        )

async def setup(bot: MadBot):
    await bot.add_cog(Sad(bot))
