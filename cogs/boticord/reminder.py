import discord

from discord.ext import commands
from discord import app_commands

from config import *
from classes import checks
from classes import db


class BoticordRemind(commands.GroupCog, group_name="remind"):
    @app_commands.command(name="info", description="Информация о напоминании")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def remind_info(self, interaction: discord.Interaction):
        user = await db.get_user(user_id=interaction.user.id)
        user_next_bump = None if user is None else user["next_bump"]
        is_enabled = "Включено" if user is not None and user["enabled"] else "Отключено"
        up_count = 0 if user is None else user["up_count"]

        embed = (
            discord.Embed(
                title=f"Напоминание о повышении - {is_enabled}",
                color=discord.Color.orange(),
                description="Бот напишет Вам в личные сообщения, когда настанет время следующего апа. "
                "**Убедитесь, что бот может написать Вам!** Для этого, откройте свои личные сообщения на одном из серверов "
                'с ботом, либо добавьте бота как пользовательское приложение, нажав "Добавить бота" в его профиле.',
            )
            .add_field(
                name="Следующий ап",
                value=(
                    f"<t:{user_next_bump}> (<t:{user_next_bump}:R>)"
                    if user_next_bump != 0
                    else "Неизвестно: бот ожидает от Вас его апа."
                ),
            )
            .add_field(name="Вы сделали апов", value=f"**{up_count:,}**")
            .set_footer(
                text="Для включения/отключения используйте /remind enable/disable."
            )
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="disable", description="Отключение напоминания о повышении"
    )
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def disable_remind(self, interaction: discord.Interaction):
        user = await db.get_user(user_id=interaction.user.id)
        if user is None or not user["enabled"]:
            embed = discord.Embed(
                title="Напоминание о повышении - Ошибка!",
                color=discord.Color.red(),
                description="У Вас уже отключены напоминания. Используйте `/remind enable` для включения напоминания.\n\n"
                "*P.s. боту необходимо дождаться, пока Вы хотя бы один раз повысите бота, чтобы начать оповещать.*",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await db.update_user(user_id=interaction.user.id, enabled=False)
        embed = discord.Embed(
            title="Напоминание о повышении - Успешно!",
            color=discord.Color.green(),
            description="Напоминания отключены. Используйте `/remind enable` для включения напоминания.\n\n"
            "*P.s. боту необходимо дождаться повышения бота после ввода команды, чтобы начать оповещать.*",
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="enable", description="Включить напоминания о повышении")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def enable_remind(self, interaction: discord.Interaction):
        user = await db.get_user(user_id=interaction.user.id)
        if user is not None and user["enabled"]:
            embed = discord.Embed(
                title="Напоминание о повышении - Ошибка!",
                color=discord.Color.red(),
                description="У Вас уже включены напоминания. Используйте `/remind disable` для отключения напоминаний.\n"
                "**Если бот не присылает напоминание**, то возможно несколько вариантов:\n"
                "- Вы ещё не повышали бота на мониторинге (либо до бота это не дошло). Проверьте это в `/remind info`.\n"
                "- Бот не может написать Вам в личные сообщения. Либо откройте их на одном из серверов с ботом, либо "
                'добавьте его как пользовательского бота, нажав "Добавить бота" в профиле бота.\n'
                "- Если ничего из этого не помогает - обратитесь в поддержку бота. Мы Вам поможем.",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        elif user is None:
            await db.add_user(user_id=interaction.user.id, reminded=True, enabled=True)
        else:
            await db.update_user(user_id=interaction.user.id, enabled=True)

        embed = discord.Embed(
            title="Напоминание о повышении - Успешно!",
            color=discord.Color.green(),
            description="- Напоминания включены. Используйте `/remind disable` для отключения напоминания.\n\n"
            "- Если Вы ни разу не повышали бота, ему надо дождаться, пока Вы повысите бота на мониторинге. "
            "После этого, бот начнёт оповещать Вас в личные сообщения. Убедитесь, что бот сможет написать Вам. "
            "Для этого нужно иметь хотя бы один общий сервер с ботом, на котором у Вас открыты личные сообщения, "
            'либо добавить его как пользовательского бота, нажав "Добавить бота" в его профиле.',
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BoticordRemind())
