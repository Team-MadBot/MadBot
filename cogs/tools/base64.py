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
    @app_commands.command(description="[Полезности] Кодирует указанный текст в Base64.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_shutted_down)
    @app_commands.describe(text="Текст для кодировки")
    async def encode(self, interaction: discord.Interaction, text: app_commands.Range[str, None, 1024]):
        ans = b64encode(text.encode()).decode()
        if len(text) > 1024 or len(ans) > 1024:
            embed = discord.Embed(
                title="Зашифровка:", 
                color=discord.Color.orange(), 
                description=f"**Исходный текст:**\n{text}"
            )
            embed1 = discord.Embed(
                title="Полученный текст:", 
                color=discord.Color.orange(), 
                description=ans
            )
            return await interaction.response.send_message(
                embeds=[embed, embed1], 
                ephemeral=True
            )
        embed = discord.Embed(
            title="Зашифровка:", 
            color=discord.Color.orange()
        ).add_field(
            name="Исходный текст:", 
            value=text, 
            inline=False
        ).add_field(
            name="Полученный текст:", 
            value=ans
        )
        await interaction.response.send_message(
            embed=embed, 
            ephemeral=True
        )

    @app_commands.command(description="[Полезности] Декодирует Base64 в текст.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_shutted_down)
    @app_commands.describe(text="Текст для декодировки")
    async def decode(self, interaction: discord.Interaction, text: str):
        try:
            ans = b64decode(text).decode()
        except Exception:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Невозможно расшифровать строку!"
            )
            return await interaction.response.send_message(
                embed=embed, 
                ephemeral=True
            )
        if len(text) > 1024 or len(ans) > 1024:
            embed = discord.Embed(
                title="Зашифровка:", 
                color=discord.Color.orange(), 
                description=f"**Исходный текст:**\n{text}"
            )
            embed1 = discord.Embed(
                title="Полученный текст:", 
                color=discord.Color.orange(), 
                description=ans
            )
            return await interaction.response.send_message(
                embeds=[embed, embed1], 
                ephemeral=True
            )
        embed = discord.Embed(
            title="Расшифровка:", 
            color=discord.Color.orange()
        ).add_field(
            name="Исходный текст:", 
            value=text, 
            inline=False
        ).add_field(
            name="Полученный текст:", 
            value=ans
        )
        await interaction.response.send_message(
            embed=embed, 
            ephemeral=True
        )

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Base64())