import discord

from discord.ext import commands
from discord import app_commands, NotFound, HTTPException
from tools import models

class Unban(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    @app_commands.command(name="unban", description="Разблокировка участника на сервере")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(
        user="Пользователь, которому необходимо убрать наказание.",
        reason="Причина разбана."
    )
    async def unban(
        self, 
        interaction: discord.Interaction, 
        user: discord.User, 
        reason: app_commands.Range[str, None, 470] = "Не указана"
    ):
        if not interaction.app_permissions.ban_members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Я не имею права на бан участников, поэтому выполнение команды невозможно."
            ).set_image(url="https://http.cat/403")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            await interaction.guild.fetch_ban(user)
        except (NotFound, HTTPException):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данный пользователь уже разбанен."
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.defer(thinking=True)
        dm_embed = discord.Embed(
            title=f"Вы разбанены на сервере {interaction.guild.name}!",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Модератор", value=f"{interaction.user.mention} (`{interaction.user}`)")
        dm_embed.add_field(name="Причина", value=reason)
        embed = dm_embed.copy()
        embed.title = "Пользователь разбанен на сервере!"
        embed.add_field(name="Пользователь", value=f"{user.mention} (`{user}`)")
        try:
            await user.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            embed.set_footer(text="Участник не получил сообщение, так как его ЛС закрыто.")
        await interaction.guild.unban(
            user=user,
            reason=reason + f" // {interaction.user}"
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: models.MadBot):
    await bot.add_cog(Unban(bot))
