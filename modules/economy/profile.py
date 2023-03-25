import discord

from discord.ext import commands
from discord import app_commands
from typing import Optional
from tools import models, db

class Profile(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @app_commands.command(name="profile", description="Получение профиля участника")
    @app_commands.describe(member="Участник, чей профиль Вы хотите увидеть")
    async def profile(self, interaction: discord.Interaction, member: Optional[discord.User]):
        if member is None: member = interaction.user
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не может иметь профиль."
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        memb = db.get_guild_user(interaction.guild.id, member.id)
        if memb is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данный пользователь не найден в базе данных этого сервера."
            ).set_image(url="https://http.cat/404")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(
            title=f"Профиль участника {member}",
            color=discord.Color.orange()
        ).set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Баланс:", value=f"`{memb.balance:,}`")
        embed.add_field(name="Уровень:", value=f"`{memb.level:,}`")
        embed.add_field(name="Опыт:", value=f"`{memb.xp:,}`")
        await interaction.response.send_message(embed=embed)

async def setup(bot: models.MadBot):
    await bot.add_cog(Profile(bot))    
