import discord
import config
import datetime
import time
import traceback
import logging

from discord.ext import commands
from discord import app_commands
from discord import Forbidden

from classes import checks
from classes import db

logger = logging.getLogger("discord")

class ErrorCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.error(self.on_error)
    
    async def cog_unload(self):
        self.bot.tree.error(self.empty_func)
    
    async def empty_func(self):
        pass

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        assert interaction.command is not None
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(),
                description=f"Задержка на команду `/{interaction.command.qualified_name}`! Попробуйте <t:{round(time.time() + error.retry_after)}:R>!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(error, app_commands.CheckFailure):
            if await checks.is_in_blacklist(interaction.user.id):
                blacklist_info = await db.get_blacklist(interaction.user.id)
                assert blacklist_info is not None
                assert interaction.user.avatar is not None
                embed = discord.Embed(
                    title="Вы занесены в чёрный список бота!",
                    color=discord.Color.red(),
                    description=f"Разработчик бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, "
                    f"обратитесь в поддержку: {config.settings['support_invite']}",
                    timestamp=datetime.datetime.now()
                ).add_field(
                    name="ID разработчика:",
                    value=blacklist_info['moderator_id']
                ).add_field(
                    name="Причина занесения в ЧС:",
                    value=blacklist_info['reason'] or "Не указана" 
                ).add_field(
                    name="ЧС закончится:",
                    value="Никогда" if blacklist_info['until'] is None else f"<t:{blacklist_info['until']}:R> (<t:{blacklist_info['until']}>)"
                ).set_thumbnail(
                    url=interaction.user.avatar.url
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if checks.is_shutted_down(interaction.command.name):
                embed = discord.Embed(title="Команда отключена!", color=discord.Color.red(),
                                    description="Владелец бота временно отключил эту команду! Попробуйте позже!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        if str(error).startswith("Failed to convert"):
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(),
                                description="Данная команда недоступна в личных сообщениях!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(error, discord.NotFound):
            return
        if isinstance(error, Forbidden):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы видите это сообщение, потому что бот не имеет прав для совершения действия!"
            )
            try:
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                return await interaction.edit_original_response(embed=embed)
        if isinstance(error, OverflowError):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Введены слишком большие числа! Введите числа поменьше!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.command.name == "calc" and (
            isinstance(error, (SyntaxError, KeyError))
        ):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Введён некорректный пример!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(),
                            description=f"Произошла неизвестная ошибка! Обратитесь в поддержку со скриншотом ошибки!\n```\n{error}```",
                            timestamp=datetime.datetime.now())
        channel = self.bot.get_channel(config.settings['log_channel'])
        assert isinstance(channel, discord.TextChannel)
        await channel.send(
            f"[ОШИБКА!]: Инициатор: `{interaction.user}`\n```\nOn command '{interaction.command.name}'\n{error}```")
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(embeds=[embed], view=None)
        logger.error(traceback.format_exception(type(error), error, error.__traceback__))

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ErrorCog(bot))
