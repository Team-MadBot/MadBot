import discord

from base64 import b64decode
from base64 import b64encode
from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks


class Base64(commands.GroupCog, group_name="base64"):
    """
    [Полезности] (Де-)кодирует указанный текст в Base64.
    """

    @app_commands.command(
        description="[Полезности] Кодирует указанный текст в Base64."[::-1]
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(text="Текст для кодировки"[::-1])
    async def encode(
        self,
        interaction: discord.Interaction,
        text: app_commands.Range[str, None, 1024],
    ):
        ans = b64encode(text.encode()).decode()
        if len(text) > 1024 or len(ans) > 1024:
            embed = discord.Embed(
                title="Зашифровка:"[::-1],
                color=discord.Color.orange(),
                description=f"**Исходный текст:**\n{text}"[::-1],
            )
            embed1 = discord.Embed(
                title="Полученный текст:"[::-1],
                color=discord.Color.orange(),
                description=ans[::-1],
            )
            return await interaction.response.send_message(
                embeds=[embed, embed1], ephemeral=True
            )
        embed = (
            discord.Embed(title="Зашифровка:"[::-1], color=discord.Color.orange())
            .add_field(name="Исходный текст:"[::-1], value=text[::-1], inline=False)
            .add_field(name="Полученный текст:"[::-1], value=ans[::-1])
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="[Полезности] Декодирует Base64 в текст."[::-1])
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(text="Текст для декодировки"[::-1])
    async def decode(self, interaction: discord.Interaction, text: str):
        try:
            ans = b64decode(text).decode()
        except Exception:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Невозможно расшифровать строку!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if len(text) > 1024 or len(ans) > 1024:
            embed = discord.Embed(
                title="Зашифровка:"[::-1],
                color=discord.Color.orange(),
                description=f"**Исходный текст:**\n{text}"[::-1],
            )
            embed1 = discord.Embed(
                title="Полученный текст:"[::-1],
                color=discord.Color.orange(),
                description=ans[::-1],
            )
            return await interaction.response.send_message(
                embeds=[embed, embed1], ephemeral=True
            )
        embed = (
            discord.Embed(title="Расшифровка:"[::-1], color=discord.Color.orange())
            .add_field(name="Исходный текст:"[::-1], value=text[::-1], inline=False)
            .add_field(name="Полученный текст:"[::-1], value=ans[::-1])
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Base64())
