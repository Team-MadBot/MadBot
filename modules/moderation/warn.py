import discord
import time
import datetime

from discord.ext import commands
from discord import app_commands
from tools import db, models

class Warn(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    @app_commands.command(name="warn", description="Выдать предупреждение участнику")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        member="Участник, которому необходимо выдать предупреждение",
        duration="Срок варна",
        reason="Причина наказания"
    )
    async def warn(
        self, 
        interaction: discord.Interaction,
        member: discord.User,
        duration: app_commands.Range[str, None, 40],
        reason: str = "Не указана"
    ) -> None:
        if not isinstance(user, discord.Member): # type: ignore
            try:
                user = await interaction.guild.fetch_member(user.id) # type: ignore
            except discord.NotFound:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Участник должен быть на сервере для выполнения данной команды."
                ).set_image(url="https://http.cat/400")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if interaction.user.top_role <= user.top_role: # type: ignore
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Ваша самая высокая роль должна быть выше самой высокой роли пользователя."
            ).set_image(url="https://http.cat/403")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        dur = 0
        duration = duration.split() # type: ignore
        for pos in duration:
            if pos[-1] not in ('d', 'h', 'm', 's') and not pos.isdigit():
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Введённая длительность варна некорректная - ввод должен соблюдать следующие параметры:\n\n"
                    "> `1.` После числа должна быть одна из букв: `d` (дни), `h` (часы), `m` (минуты) и `s` (секунды). Если "
                    "буква отсутствует, бот сочтёт число за кол-во секунд.\n"
                    "> `2.` Числа должны быть разделены пробелами (пример: `1d 43m 34`).\n"
                    "> `3.` Суммарная продолжительность варна не должена превышать 1 год.\n"
                    "> `4.` Нельзя дать варн на 0 секунд или на отрицательное кол-во времени."
                ).set_image(url="https://http.cat/400.jpg")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            k = 1
            if pos[-1] == 'd': k = 3600 * 24
            if pos[-1] == 'h': k = 3600
            if pos[-1] == 'm': k = 60
            if pos.isdigit():
                dur += int(pos)
                continue
            try:
                dur += int(pos[:-1]) * k
            except:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Введённая длительность варна некорректная - ввод должен соблюдать следующие параметры:\n\n"
                    "> `1.` После числа должна быть одна из букв: `d` (дни), `h` (часы), `m` (минуты) и `s` (секунды). Если "
                    "буква отсутствует, бот сочтёт число за кол-во секунд.\n"
                    "> `2.` Числа должны быть разделены пробелами (пример: `1d 43m 34`).\n"
                    "> `3.` Суммарная продолжительность варна не должена превышать 1 год.\n"
                    "> `4.` Нельзя дать варн на 0 секунд или на отрицательное кол-во времени."
                ).set_image(url="https://http.cat/400.jpg")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        if dur > 12 * 30 * 24 * 3600 or dur <= 0:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Введённая длительность варна некорректная - ввод должен соблюдать следующие параметры:\n\n"
                "> `1.` После числа должна быть одна из букв: `d` (дни), `h` (часы), `m` (минуты) и `s` (секунды). Если "
                "буква отсутствует, бот сочтёт число за кол-во секунд.\n"
                "> `2.` Числа должны быть разделены пробелами (пример: `1d 43m 34`).\n"
                "> `3.` Суммарная продолжительность варна не должена превышать 1 год.\n"
                "> `4.` Нельзя дать варн на 0 секунд или на отрицательное кол-во времени."
            ).set_image(url="https://http.cat/400.jpg")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        until = round(time.time()) + dur
        await interaction.response.defer(thinking=True)
        dm_embed = discord.Embed(
            title=f"Вы получили варн на сервере {interaction.guild.name}!", # type: ignore
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Модератор", value=f"{interaction.user.mention} (`{interaction.user}`)")
        dm_embed.add_field(name="Время истечения", value=f"<t:{round(time.time()) + dur}> (<t:{round(time.time()) + dur}:R>)")
        dm_embed.add_field(name="Причина", value=reason)
        embed = dm_embed.copy()
        embed.title = "Пользователь получил варн на сервере!"
        embed.add_field(name="Пользователь", value=f"{user.mention} (`{user}`)")
        try:
            await user.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            embed.set_footer(text="Участник не получил сообщение, так как его ЛС закрыто.")
        db.warn_user(
            models.UserWarn(
                guild_id=interaction.guild.id, # type: ignore
                user_id=member.id, 
                mod_id=interaction.user.id,
                until=until,
                reason=reason
            )
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: models.MadBot):
    await bot.add_cog(Warn(bot))
