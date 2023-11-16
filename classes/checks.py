import discord
from discord.ext import commands
from config import *
from classes import db as mongo_db # костылю

def isPremium(bot: commands.Bot, user_id: int) -> str:
    """
    Узнать, является ли пользователь премиум-пользователем.
    
    Возвращает:
    - 'server' - пользователь имеет подписку Premium Server.
    - 'user' - пользователь имеет подписку Premium User.
    - 'None' - пользователь не имеет подписки.
    """
    db = client.premium
    coll = db.user
    isPrem = coll.find_one({'user_id': str(user_id)})
    if isPrem is None: isPrem = {'type': 'None'}
    return isPrem['type']

def isPremiumServer(bot: commands.Bot, guild: discord.Guild) -> bool:
    """
    Узнать, имеет ли сервер премиум-подписку.

    Возвращает:
    - Истину или ложь.
    """
    db = client.premium
    coll = db.guild
    isPrem = coll.find_one({'guild_id': str(guild.id)})
    if isPrem is not None and isPremium(bot, isPrem['user_id']) is None: coll.delete_one({'user_id': isPrem['user_id']})
    return isPrem is not None and isPremium(bot, isPrem['user_id']) != 'None'

def is_in_blacklist(resource_id: int) -> bool:
    return bool(mongo_db.get_blacklist(resource_id))

def is_shutted_down(command: str) -> bool:
    return bool(mongo_db.get_shutted_command(command))

