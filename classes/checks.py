import discord
from discord.ext import commands
from config import *
from classes import db as mongo_db # костылю

def isPremium(bot: commands.Bot, user_id: int) -> str:
    """Checks if a user is a premium user of the bot.

    Args:
        bot (commands.Bot): The bot instance.
        user_id (int): The Discord ID of the user.

    Returns:
        str: The premium type if the user is premium, else 'None'.
    """
    db = client.premium
    coll = db.user
    isPrem = coll.find_one({'user_id': str(user_id)})
    if isPrem is None: isPrem = {'type': 'None'}
    return isPrem['type']

def isPremiumServer(bot: commands.Bot, guild: discord.Guild) -> bool:
    """Checks if a Discord guild has premium status.

    Args:
        bot (commands.Bot): The Discord bot instance.
        guild (discord.Guild): The guild to check premium status for.

    Returns:
        bool: True if the guild has premium, False otherwise.
    """
    db = client.premium
    coll = db.guild
    isPrem = coll.find_one({'guild_id': str(guild.id)})
    if isPrem is not None and isPremium(bot, isPrem['user_id']) is None: coll.delete_one({'user_id': isPrem['user_id']})
    return isPrem is not None and isPremium(bot, isPrem['user_id']) != 'None'

def is_in_blacklist(resource_id: int) -> bool:
    """Checks if a resource ID is in the blacklist.

    Args:
        resource_id (int): The resource ID to check.

    Returns:
        bool: True if the resource ID is in the blacklist, False otherwise.
    """
    return bool(mongo_db.get_blacklist(resource_id))


def is_shutted_down(command: str) -> bool:
    """Checks if a command is currently shut down.

    Args:
        command (str): The name of the command to check.

    Returns:
        bool: True if the command is shut down, False otherwise.
    """
    return bool(mongo_db.get_shutted_command(command))
