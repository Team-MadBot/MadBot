from typing import Optional

import discord
from discord import app_commands

from classes.checks import isPremium, isPremiumServer


async def default_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (await isPremium(interaction.client, interaction.user.id) != 'None' or
            await isPremiumServer(interaction.client, interaction.guild)):
        return None
    return app_commands.Cooldown(1, 3.0)


async def hard_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (await isPremium(interaction.client, interaction.user.id) != 'None' or
            await isPremiumServer(interaction.client, interaction.guild)):
        return app_commands.Cooldown(1, 2.0)
    return app_commands.Cooldown(1, 10.0)