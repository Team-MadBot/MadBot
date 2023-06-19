import time

from . import database
from tools import models
from typing import (
    Optional
)
from tools.models import (
    UserWarn,
    UserUnwarn
)

def warn_user(action: UserWarn):
    coll = database.guild
    guild_id = action.guild_id
    user_id = action.user_id
    mod_id = action.mod_id
    until = action.until
    reason = action.reason

    guild = coll.find_one({'guild_id': str(guild_id)})

    if guild is None:
        coll.insert_one(
            {
                'guild_id': str(guild_id),
                'members': [
                    {
                        'user_id': str(user_id),
                        'balance': 0,
                        'level': 0,
                        'xp': 0,
                        'actions': [
                            {
                                'id': 4,
                                'user_id': str(user_id),
                                'mod_id': str(mod_id),
                                'time': round(time.time()),
                                'until': until,
                                'reason': reason
                            }
                        ],
                        'inventory': []
                    }
                ],
                'autoroles': [],
                'buttonroles': [],
                'items': []
                
            }
        )
        return True
    
    user = next((item for item in guild['members'] if item["user_id"] == str(user_id)), None)
    if user is None:
        coll.update_one(
            {'guild_id': str(guild_id)},
            {
                "$push": {
                    'members': {
                        'user_id': str(user_id),
                        'balance': 0,
                        'level': 0,
                        'xp': 0,
                        'actions': [
                            {
                                'id': 4,
                                'user_id': str(user_id),
                                'mod_id': str(mod_id),
                                'time': round(time.time()),
                                'until': until,
                                'reason': reason
                            }
                        ],
                        'inventory': []
                    }
                }
            } 
        )
        return True
    coll.update_many(
        {
            'guild_id': str(guild_id),
            'members': {
                "$elemMatch": {
                    'user_id': str(user_id)
                }
            }
        },
        {
            "$push": {
                "members.$.actions": {
                    'id': 4,
                    'user_id': str(user_id),
                    'mod_id': str(mod_id),
                    'time': round(time.time()),
                    'until': until,
                    'reason': reason
                }
            }
        }
    )
    return True

def remove_last_warn(action: UserUnwarn) -> bool:
    coll = database.guild
    guild_id = action.guild_id
    user_id = action.user_id
    mod_id = action.mod_id
    reason = action.reason

    guild = coll.find_one({'guild_id': str(guild_id)})

    if guild is None:
        return False
    
    user = next((item for item in guild['members'] if item["user_id"] == str(user_id)), None)
    if user is None:
        return False
    
    coll.update_many(
        {
            'guild_id': str(guild_id),
            'members': {
                "$elemMatch": {
                    'user_id': str(user_id)
                }
            }
        },
        {
            "$push": {
                "members.$.actions": {
                    'id': 5,
                    'user_id': str(user_id),
                    'mod_id': str(mod_id),
                    'time': round(time.time()),
                    'reason': reason
                }
            }
        }
    )
    return True

def get_guild(guild_id: int) -> Optional[models.BotGuild]:
    coll = database.guild
    guild = coll.find_one(
        {"guild_id": str(guild_id)}
    )
    if guild is None: return None
    return models.BotGuild(
        guild_id=guild_id,
        members=[models.GuildUser.from_dict(user, guild_id) for user in guild['members']],
        items=[models.GuildItem.from_dict(guild_id, item) for item in guild['items']],
        autoroles=[int(role_id) for role_id in guild['autoroles']],
        buttonroles=[models.ButtonRole.from_dict(brole) for brole in guild['buttonroles']]
    )
