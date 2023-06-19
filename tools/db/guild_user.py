from . import database
from typing import Optional
from tools import models
from tools.models import (
    GuildUser,
    GuildItem,
    EditMoneyAction
)

def get_guild_user(guild_id: int, user_id: int) -> Optional[GuildUser]:
    coll = database.guild
    guild = coll.find_one({'guild_id': str(guild_id)})
    if guild is None: return None
    user = [memb for memb in guild['members'] if memb['user_id'] == str(user_id)]
    if len(user) == 0: return None
    user = user[0]
    return GuildUser(
        guild_id, 
        user_id, 
        user['balance'], 
        user['xp'], 
        user['level'], 
        [GuildItem.from_dict(guild_id, item) for item in user['inventory']]
    )

def update_money(action: EditMoneyAction) -> bool:
    coll = database.guild
    guild_id = action.guild_id
    amount = action.amount

    guild = coll.find_one({'guild_id': str(guild_id)})
    if action.id == models.GuildActionsType.TRANSFER:
        if guild is None:
            return False
        
        from_id = action.from_id # type: ignore
        to_id = action.to_id # type: ignore

        from_user = next((item for item in guild['members'] if item["user_id"] == str(from_id)), None)
        to_user = next((item for item in guild['members'] if item["user_id"] == str(to_id)), None)
        if from_user is None:
            return False
        if to_user is None:
            coll.update_many(
                {
                    'guild_id': str(guild_id),
                    'members': {
                        "$elemMatch": {
                            'user_id': str(from_id)
                        }
                    }
                },
                {
                    "$inc": {
                        "members.$.balance": -amount
                    },
                    "$push": {
                        "members.$.actions": action.to_dict()
                    }
                }
            )
            coll.update_one(
                {'guild_id': str(guild_id)},
                {
                    "$push": {
                        'members': {
                            'user_id': str(to_id),
                            'balance': amount,
                            'level': 0,
                            'xp': 0,
                            'actions': [action.to_dict()],
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
                        'user_id': str(from_id)
                    }
                }
            },
            {
                "$inc": {
                    "members.$.balance": -amount
                },
                "$push": {
                    "members.$.actions": action.to_dict()
                }
            }
        )
        coll.update_many(
            {
                'guild_id': str(guild_id),
                'members': {
                    "$elemMatch": {
                        'user_id': str(to_id)
                    }
                }
            },
            {
                "$inc": {
                    "members.$.balance": amount
                },
                "$push": {
                    "members.$.actions": action.to_dict()
                }
            }
        )
        return True

    user_id = action.user_id
    if guild is None:
        coll.insert_one(
            {
                'guild_id': str(guild_id),
                'members': [
                    {
                        'user_id': str(user_id),
                        'balance': amount,
                        'level': 0,
                        'xp': 0,
                        'actions': [action.to_dict()],
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
                        'balance': amount,
                        'level': 0,
                        'xp': 0,
                        'actions': [action.to_dict()],
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
            "$inc": {
                "members.$.balance": amount
            },
            "$push": {
                "members.$.actions": action.to_dict()
            }
        }
    )
    return True