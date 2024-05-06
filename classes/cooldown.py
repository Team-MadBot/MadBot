import discord
import time

from typing import Optional

from discord import app_commands

from classes import db
from classes.checks import is_premium, is_premium_server

async def default_cooldown(
    interaction: discord.Interaction,
) -> Optional[app_commands.Cooldown]:
    assert interaction.guild is not None
    if await is_premium(interaction.user.id) != "None" or await is_premium_server(
        interaction.guild
    ) or ((await db.get_user(interaction.user.id)) or {'next_bump': 0})['next_bump'] > time.time():
        return None
    return app_commands.Cooldown(1, 3.0)


async def hard_cooldown(
    interaction: discord.Interaction,
) -> Optional[app_commands.Cooldown]:
    assert interaction.guild is not None
    if await is_premium(interaction.user.id) != "None" or await is_premium_server(
        interaction.guild
    ) or ((await db.get_user(interaction.user.id)) or {'next_bump': 0})['next_bump'] > time.time():
        return app_commands.Cooldown(1, 2.0)
    return app_commands.Cooldown(1, 10.0)
