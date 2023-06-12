import discord
import time
import datetime

from discord.ext import commands
from discord import app_commands
from tools import db, models

class Unwarn(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    @app_commands.command(name="unward", description="Снимает последнее предупреждение участника")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        member="Участник, которому необходимо выдать предупреждение",
        reason="Причина снятия варна"
    )
    async def unwarn(
        self, 
        interaction: discord.Interaction,
        member: discord.User,
        reason: str = "Не указана"
    ) -> None:
        await interaction.response.defer(thinking=True)
        dm_embed = discord.Embed(
            title=f"С Вас снят последний варн на сервере {interaction.guild.name}!", # type: ignore
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Модератор", value=f"{interaction.user.mention} (`{interaction.user}`)")
        dm_embed.add_field(name="Причина", value=reason)
        embed = dm_embed.copy()
        embed.title = "С пользователя снят варн на сервере!"
        embed.add_field(name="Пользователь", value=f"{member.mention} (`{member}`)")
        try:
            await member.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            embed.set_footer(text="Участник не получил сообщение, так как его ЛС закрыто.")
        db.remove_last_warn(
            models.UserUnwarn(
                guild_id=interaction.guild.id, # type: ignore
                user_id=member.id,
                mod_id=interaction.user.id,
                reason=reason
            )
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: models.MadBot):
    await bot.add_cog(Unwarn(bot))
