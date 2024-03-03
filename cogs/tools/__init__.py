import discord

from typing import Optional
from classes.checks import is_premium, is_premium_server
from discord import app_commands

async def default_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (await is_premium(interaction.user.id) != 'None' or (
            interaction.guild and await is_premium_server(interaction.guild))):
        return None
    return app_commands.Cooldown(1, 3.0)


async def hard_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (await is_premium(interaction.user.id) != 'None' or (
            interaction.guild and await is_premium_server(interaction.guild))):
        return app_commands.Cooldown(1, 2.0)
    return app_commands.Cooldown(1, 10.0)