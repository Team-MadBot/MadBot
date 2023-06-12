import discord
import datetime

from discord import app_commands
from discord.ext import commands
from tools import models
from checks import cooldown
from typing import Optional

class Clear(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @app_commands.command(name="clear", description="Очистка канала от N сообщений")
    @app_commands.guild_only()
    @app_commands.checks.dynamic_cooldown(cooldown.clear)
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    @app_commands.describe(
        amount="Кол-во сообщений для очистки", 
        user="Пользователь, чьи сообщения надо очистить"
    )
    async def clear(
        self, 
        interaction: discord.Interaction, 
        amount: app_commands.Range[int, 2, 100],
        user: Optional[discord.User]
    ):
        await interaction.response.defer(thinking=True, ephemeral=True)
        if user is not None:
            after = discord.utils.utcnow() - datetime.timedelta(weeks=2)
            delete_messages = [
                msg async for msg in interaction.channel.history( # type: ignore
                    limit=None,
                    after=after,
                    oldest_first=False
                ) if msg.author.id == user.id
            ]
            if len(delete_messages) == 0:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Сообщений за последние 2 недели в этом канале от данного пользователя нет."
                ).set_image(url="https://http.cat/404")
                return await interaction.followup.send(embed=embed, ephemeral=True)
            delete_messages = delete_messages[:amount]
            try:
                await interaction.channel.delete_messages(delete_messages, reason=str(interaction.user)) # type: ignore
            except discord.Forbidden:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="У бота забрали право на очистку сообщений во время работы!"
                ).set_image(url="https://http.cat/403")
                return await interaction.followup.send(embed=embed, ephemeral=True)
            embed = discord.Embed(
                title="Очистка - Итог",
                color=discord.Color.green() if len(delete_messages) == amount else discord.Color.yellow(),
                description=(
                    f"Было очищено `{len(delete_messages)}` сообщений от {user.mention}." + ("" if len(delete_messages) == amount else
                    f" `{amount - len(delete_messages)}` сообщений не было удалено из-за давности сообщений (либо сообщения "
                    "просто закончились).")
                )
            )
            msg = await interaction.followup.send(embed=embed, wait=True)
            return await msg.delete(delay=30)
        try:
            deleted = await interaction.channel.purge( # type: ignore
                limit=amount,
                check=lambda m: m.created_at.astimezone(discord.utils.utcnow().tzinfo) > discord.utils.utcnow() - datetime.timedelta(weeks=2),
                reason=str(interaction.user)
            )
        except discord.Forbidden:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У бота забрали право на очистку сообщений или на просмотр истории сообщений во время работы!"
            ).set_image(url="https://http.cat/403")
            return await interaction.followup.send(embed=embed, ephemeral=True)
        embed = discord.Embed(
            title="Очистка - Итог",
            color=discord.Color.green() if len(deleted) == amount else discord.Color.yellow(),
            description=(
                f"Было очищено `{len(deleted)}` сообщений." + ("" if len(deleted) == amount else
                f" `{amount - len(deleted)}` сообщений не было удалено из-за давности сообщений (либо сообщения "
                "просто закончились).")
            )
        )
        msg = await interaction.followup.send(embed=embed, wait=True)
        try:
            await msg.delete(delay=30)
        except:
            pass

async def setup(bot: models.MadBot):
    await bot.add_cog(Clear(bot))
