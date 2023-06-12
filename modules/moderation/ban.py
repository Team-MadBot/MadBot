import discord

from discord.ext import commands
from discord import app_commands
from tools import models

class Ban(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    @app_commands.command(name="ban", description="Блокировка участника на сервере")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(
        user="Пользователь, которому необходимо выдать наказание.",
        reason="Причина наказания.",
        delete_message_days="За сколько последних дней надо удалить сообщения?"
    )
    async def ban(
        self, 
        interaction: discord.Interaction, 
        user: discord.User, 
        reason: app_commands.Range[str, None, 470] = "Не указана",
        delete_message_days: app_commands.Range[int, None, 7] = 0
    ):
        if not interaction.app_permissions.ban_members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Я не имею права на бан участников, поэтому выполнение команды невозможно."
            ).set_image(url="https://http.cat/403")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not isinstance(user, discord.Member):
            try:
                user = await interaction.guild.fetch_member(user.id) # type: ignore
            except discord.NotFound:
                pass
            else:
                bot_member = await interaction.guild.fetch_member(self.bot.user.id) # type: ignore
                if bot_member.top_role <= user.top_role: # type: ignore
                    embed = discord.Embed(
                        title="Ошибка!",
                        color=discord.Color.red(),
                        description="Самая высокая роль бота должна быть выше самой высокой роли пользователя."
                    ).set_image(url="https://http.cat/403")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                if interaction.user.top_role <= user.top_role: # type: ignore
                    embed = discord.Embed(
                        title="Ошибка!",
                        color=discord.Color.red(),
                        description="Ваша самая высокая роль должна быть выше самой высокой роли пользователя."
                    ).set_image(url="https://http.cat/403")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.defer(thinking=True)
        dm_embed = discord.Embed(
            title=f"Вы забанены на сервере {interaction.guild.name}!", # type: ignore
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Модератор", value=f"{interaction.user.mention} (`{interaction.user}`)")
        dm_embed.add_field(name="Причина", value=reason)
        embed = dm_embed.copy()
        embed.title = "Пользователь забанен на сервере!"
        embed.add_field(name="Пользователь", value=f"{user.mention} (`{user}`)")
        try:
            await user.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            embed.set_footer(text="Участник не получил сообщение, так как его ЛС закрыто.")
        await interaction.guild.ban( # type: ignore
            user=user,
            reason=reason + f" // {interaction.user}", 
            delete_message_days=delete_message_days
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: models.MadBot):
    await bot.add_cog(Ban(bot))
