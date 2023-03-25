import discord

from discord.ext import commands
from discord import app_commands
from tools import models

def test_cd(interaction: discord.Interaction):
    return app_commands.Cooldown(1, 10.0)

class TestCog(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @app_commands.command(name="test", description="тест кд")
    @app_commands.checks.dynamic_cooldown(test_cd)
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("https://http.cat/200")

async def setup(bot: models.MadBot):
    await bot.add_cog(TestCog(bot))
