import discord

from discord import app_commands
from typing import Optional

def clear(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    return app_commands.Cooldown(1, 10.0)
