import discord

from discord.ext import commands
from discord import app_commands
from tools import db, models

class Remove_Money(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @app_commands.command(name="remove-money", description="Убрать монеты у участника")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(member="Участник, кому надо убрать денег", money="Кол-во валюты")
    async def remove_money(self, interaction: discord.Interaction, member: discord.User, money: app_commands.Range[int, 1, None]):
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Давай подумаем логически: откуда у бота могут быть деньги?"
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        user = db.get_guild_user(interaction.guild.id, member.id) # type: ignore
        if user is None or user.balance < money:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Нельзя допускать отрицательного баланса!"
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        db.update_money(
            models.PatchMoneyAction(
                guild_id=interaction.guild.id, # type: ignore
                user_id=member.id,
                patcher_id=interaction.user.id,
                reason="/remove-money command",
                amount=-money
            )
        )
        embed = discord.Embed(
            title="Отнятие денег - Успешно!",
            color=discord.Color.green(),
            description=f"У участника {member.mention} отобрано `{money:,}` монет администратором {interaction.user.mention}."
        )
        await interaction.response.send_message(embed=embed)
    
async def setup(bot: models.MadBot):
    await bot.add_cog(Remove_Money(bot))
