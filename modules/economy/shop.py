import discord

from discord import app_commands
from discord.ext import commands
from tools import models, db

class EconomyShop(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    @app_commands.command(name="shop", description="Магазин сервера")
    @app_commands.guild_only()
    async def shop(self, interaction: discord.Interaction):
        guild = db.get_guild(interaction.guild.id)
        if guild is None or guild.items == []:
            embed = discord.Embed(
                title="Магазин сервера (0).",
                color=discord.Color.orange(),
                description="*Пусто...*"
            ).set_image("https://http.cat/204")
            return await interaction.response.send_message(embed=embed)


async def setup(bot: models.MadBot):
    await bot.add_cog(EconomyShop(bot))
