import discord

from discord.ext import commands
from discord import app_commands

from config import *
from classes import checks
from classes import db

class BoticordRemind(commands.GroupCog, group_name="remind"):
    @app_commands.command(name="info", description="Информация о напоминании")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def remind_info(self, interaction: discord.Interaction):
        user = db.get_user(user_id=interaction.user.id)
        user_next_bump = None if user is None else user['next_bump']
        is_enabled = "Включено" if user is not None and user['enabled'] else "Отключено"
        up_count = 0 if user is None else user['up_count']

        embed = discord.Embed(
            title=f"Напоминание о повышении - {is_enabled}",
            color=discord.Color.orange(),
            description="Бот должен упомянуть Вас в канале <#1064172930390556672>, когда настанет "
            "время следующего апа."
        ).add_field(
            name="Следующий ап",
            value=f"<t:{user_next_bump}> (<t:{user_next_bump}:R>)" if user_next_bump != 0 else "Неизвестно, апните бота."
        ).add_field(
            name="Вы сделали апов",
            value=f"**{up_count:,}**"
        ).set_footer(
            text="Для включения/отключения используйте /remind enable/disable."
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="disable", description="Отключение напоминания о повышении")
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def disable_remind(self, interaction: discord.Interaction):
        user = db.get_user(user_id=interaction.user.id)
        if user is None or not user['enabled']:
            embed = discord.Embed(
                title="Напоминание о повышении - Ошибка!",
                color=discord.Color.red(),
                description="У Вас отключены напоминания. Используйте `/remind enable` для включения напоминания.\n\n"
                "*P.s. боту необходимо дождаться, пока Вы хотя бы один раз повысите бота, чтобы начать оповещать.*"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        db.update_user(user_id=interaction.user.id, enabled=False)
        embed = discord.Embed(
            title="Напоминание о повышении - Успешно!",
            color=discord.Color.green(),
            description="Напоминания отключены. Используйте `/remind enable` для включения напоминания.\n\n"
            "*P.s. боту необходимо дождаться повышения бота после ввода команды, чтобы начать оповещать.*"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="enable", description="Включить напоминания о повышении")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def enable_remind(self, interaction: discord.Interaction):
        user = db.get_user(user_id=interaction.user.id)
        if user is not None and user['enabled']:
            embed = discord.Embed(
                title="Напоминание о повышении - Ошибка!",
                color=discord.Color.red(),
                description="У Вас уже включены напоминания. Используйте `/remind disable` для отключения напоминаний."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        elif user is None:
            db.add_user(
                user_id=interaction.user.id,
                reminded=True, 
                enabled=True
            )
        else:
            db.update_user(user_id=interaction.user.id, enabled=True)
        
        embed = discord.Embed(
            title="Напоминание о повышении - Успешно!",
            color=discord.Color.green(),
            description="- Напоминания включены. Используйте `/remind disable` для отключения напоминания.\n\n"
            "- Если Вы ни разу не повышали бота после 4 июля, боту надо дождаться, "
            "пока вы повысите бота на мониторинге. После этого, бот начнёт оповещать Вас "
            "в канале <#1064172930390556672> на сервере поддержки. Для того, чтобы видеть канал, выберите в "
            "вопросе \"С какой целью Вы зашли на сервер?\" пункт \"Поддержка бота\"."
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BoticordRemind())
