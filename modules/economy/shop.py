import discord

from discord import app_commands
from discord.ext import commands
from tools import models

class EconomyShop(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    @app_commands.command(name="shop", description="Магазин сервера")
    @app_commands.guild_only()
    async def shop(self, interaction: discord.Interaction):
        pass

async def setup(bot: models.MadBot):
    await bot.add_cog(EconomyShop(bot))
