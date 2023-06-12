import discord
import time
import datetime

from discord.ext import commands
from discord import app_commands
from tools import models

class Timeout(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot

    @app_commands.command(name="timeout", description="Отправить участника в мут.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        user="Пользователь, которому необходимо выдать наказание.",
        reason="Причина наказания.",
        duration="Срок действия мута."
    )
    async def timeout(
        self, 
        interaction: discord.Interaction, 
        user: discord.User, 
        duration: app_commands.Range[str, None, 40],
        reason: app_commands.Range[str, None, 470] = "Не указана"
    ):
        if not isinstance(user, discord.Member):
            try:
                user = await interaction.guild.fetch_member(user.id) # type: ignore
            except discord.NotFound:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Участник должен быть на сервере для выполнения данной команды."
                ).set_image(url="https://http.cat/400")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not interaction.app_permissions.moderate_members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Я не имею права на мут участников, поэтому выполнение команды невозможно."
            ).set_image(url="https://http.cat/403")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if user.is_timed_out(): # type: ignore
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Пользователь уже замучен. Размутьте для перевыдачи наказания."
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
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
        if user.guild_permissions.administrator: # type: ignore
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Невозможно замутить администратора."
            ).set_image(url="https://http.cat/403")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        dur = 0
        duration = duration.split() # type: ignore
        for pos in duration:
            if pos[-1] not in ('d', 'h', 'm', 's') and not pos.isdigit():
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Введённая длительность тайм-аута некорректная - ввод должен соблюдать следующие параметры:\n\n"
                    "> `1.` После числа должна быть одна из букв: `d` (дни), `h` (часы), `m` (минуты) и `s` (секунды). Если "
                    "буква отсутствует, бот сочтёт число за кол-во секунд.\n"
                    "> `2.` Числа должны быть разделены пробелами (пример: `1d 43m 34`).\n"
                    "> `3.` Суммарная продолжительность тайм-аута не должена превышать 28 дней.\n"
                    "> `4.` Нельзя замутить на 0 секунд или на отрицательное кол-во времени."
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
                    description="Введённая длительность тайм-аута некорректная - ввод должен соблюдать следующие параметры:\n\n"
                    "> `1.` После числа должна быть одна из букв: `d` (дни), `h` (часы), `m` (минуты) и `s` (секунды). Если "
                    "буква отсутствует, бот сочтёт число за кол-во секунд.\n"
                    "> `2.` Числа должны быть разделены пробелами (пример: `1d 43m 34`).\n"
                    "> `3.` Суммарная продолжительность тайм-аута не должена превышать 28 дней.\n"
                    "> `4.` Нельзя замутить на 0 секунд или на отрицательное кол-во времени."
                ).set_image(url="https://http.cat/400.jpg")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        if dur > 28 * 24 * 3600 or dur <= 0:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Введённая длительность тайм-аута некорректная - ввод должен соблюдать следующие параметры:\n\n"
                "> `1.` После числа должна быть одна из букв: `d` (дни), `h` (часы), `m` (минуты) и `s` (секунды). Если "
                "буква отсутствует, бот сочтёт число за кол-во секунд.\n"
                "> `2.` Числа должны быть разделены пробелами (пример: `1d 43m 34`).\n"
                "> `3.` Суммарная продолжительность тайм-аута не должена превышать 28 дней.\n"
                "> `4.` Нельзя замутить на 0 секунд или на отрицательное кол-во времени."
            ).set_image(url="https://http.cat/400.jpg")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.defer(thinking=True)
        dm_embed = discord.Embed(
            title=f"Вы замучены на сервере {interaction.guild.name}!", # type: ignore
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Модератор", value=f"{interaction.user.mention} (`{interaction.user}`)")
        dm_embed.add_field(name="Время истечения", value=f"<t:{round(time.time()) + dur}> (<t:{round(time.time()) + dur}:R>)")
        dm_embed.add_field(name="Причина", value=reason)
        embed = dm_embed.copy()
        embed.title = "Пользователь замучен на сервере!"
        embed.add_field(name="Пользователь", value=f"{user.mention} (`{user}`)")
        try:
            await user.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            embed.set_footer(text="Участник не получил сообщение, так как его ЛС закрыто.")
        await user.edit( # type: ignore
            timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=dur),
            reason=reason + f" // {interaction.user}"
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: models.MadBot):
    await bot.add_cog(Timeout(bot))
