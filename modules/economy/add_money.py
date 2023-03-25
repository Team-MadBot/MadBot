import discord

from discord.ext import commands
from discord import app_commands
from tools import db, models

class Add_Money(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @app_commands.command(name="add-money", description="Добавить монет участнику")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(member="Участник, кому надо выдать деньги", money="Кол-во валюты")
    async def add_money(self, interaction: discord.Interaction, member: discord.User, money: app_commands.Range[int, 1, None]):
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Давай подумаем логически: зачем боту деньги?"
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not isinstance(member, discord.Member):
            try:
                member = await interaction.guild.fetch_member(member.id)
            except discord.NotFound:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Выполнение данной команды возможно только на участнике, который есть на сервере."
                ).set_image(url="https://http.cat/400")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        db.update_money(interaction.guild.id, member.id, money)
        embed = discord.Embed(
            title="Выдача денег - Успешно!",
            color=discord.Color.green(),
            description=f"Участнику {member.mention} выдано `{money:,}` монет администратором {interaction.user.mention}."
        )
        await interaction.response.send_message(embed=embed)
    
async def setup(bot: models.MadBot):
    await bot.add_cog(Add_Money(bot))
