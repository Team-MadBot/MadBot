import discord

from typing import Optional
from classes.checks import isPremium, isPremiumServer
from discord import app_commands

def default_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (isPremium(interaction.client, interaction.user.id) != 'None' or
            isPremiumServer(interaction.client, interaction.guild)):
        return None
    return app_commands.Cooldown(1, 3.0)


def hard_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (isPremium(interaction.client, interaction.user.id) != 'None' or
            isPremiumServer(interaction.client, interaction.guild)):
        return app_commands.Cooldown(1, 2.0)
    return app_commands.Cooldown(1, 10.0)