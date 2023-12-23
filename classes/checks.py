import discord

from discord.ext import commands

from config import *
from classes import db

async def isPremium(bot: commands.AutoShardedBot, user_id: int) -> str:
    """Checks if a user is a premium user of the bot.

    Args:
        bot (commands.Bot): The bot instance.
        user_id (int): The Discord ID of the user.

    Returns:
        str: The premium type if the user is premium, else 'None'.
    """
    isPrem = await db.get_premium_user(user_id=user_id)
    return isPrem.get('type', 'None')

async def isPremiumServer(bot: commands.AutoShardedBot, guild: discord.Guild) -> bool:
    """Checks if a Discord guild has premium status.

    Args:
        bot (commands.Bot): The Discord bot instance.
        guild (discord.Guild): The guild to check premium status for.

    Returns:
        bool: True if the guild has premium, False otherwise.
    """
    isPrem = await db.get_premium_guild_info(guild_id=guild.id)
    if isPrem is not None and await isPremium(bot, isPrem.get("user_id")) == 'None': await db.take_guild_premium(guild_id=guild.id)
    return isPrem is not None and await isPremium(bot, isPrem.get("user_id")) != 'None'

async def is_in_blacklist(resource_id: int) -> bool:
    """Checks if a resource ID is in the blacklist.

    Args:
        resource_id (int): The resource ID to check.

    Returns:
        bool: True if the resource ID is in the blacklist, False otherwise.
    """
    return bool(await db.get_blacklist(resource_id))

async def interaction_is_not_in_blacklist(interaction: discord.Interaction) -> bool:
    """Checks if a resource ID isn't in the blacklist, but for discord.py's `checks` function
    
    Args:
        interaction (discord.Interaction): Discord's interaction class.
        
    Returns:
        bool: Is check successful.
    """
    return not await is_in_blacklist(resource_id=interaction.user.id)

async def is_shutted_down(command: str) -> bool:
    """Checks if a command is currently shut down.

    Args:
        command (str): The name of the command to check.

    Returns:
        bool: True if the command is shut down, False otherwise.
    """
    return bool(await db.get_shutted_command(command))

async def interaction_is_not_shutted_down(interaction: discord.Interaction) -> bool:
    """Checks if a command isn't currently shut down, but for discord.py's `checks` function
    
    Args:
        interaction (discord.Interaction): Discord's interaction class.
        
    Returns:
        bool: Is check successful.
    """
    return not await is_shutted_down(command=interaction.command.name)
