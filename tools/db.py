"""
This is database callback code. You can see the structure of collections:

1. Blacklist:
{
    'user_id': str,
    'blocked_at': int,
    'reason': str,
    'blocked_at': Optional[str]
}

2. GuildMemberAction:
{
    'type': int,
    ...and other stuff for specific action
}

3. GuildMember:
{
    'user_id': str,
    'balance': int,
    'level': int,
    'xp': int,
    'actions': List[GuildMemberAction]
}

4. ButtonRole:
{
    'channel_id': str,
    'message_id': str,
    'type': str in ("single", "multiple")
    'roles': List[str]
}

5. Guild:
{
    'guild_id': str,
    'members': List[GuildMember],
    'autoroles': List[str],
    'buttonroles': List[ButtonRole]
}
"""
import time

from pymongo import MongoClient
from config import settings
from tools import models
from tools.models import BlackList
from tools.models import GuildUser
from tools.models import EditMoneyAction
from tools.models import UserWarn, UserUnwarn
from typing import Optional

# db init
client = MongoClient() if settings['mongo_url'] is None else MongoClient(settings['mongo_url'])
db = client.madbotv2

def check_blacklist(user_id: int) -> bool:
    # you can find collection's structure at line 4 (collection 1).
    coll = db.blacklist
    return bool(coll.find_one({"user_id": str(user_id)}))

def get_blacklist(user_id: int) -> Optional[BlackList]:
    # you can find collection's structure at line 4 (collection 1).
    coll = db.blacklist
    blacklist = coll.find_one({"user_id": str(user_id)})
    if blacklist is None: return None
    return BlackList(
        int(blacklist['user_id']), 
        blacklist['blocked_at'],
        blacklist['reason'],
        blacklist['blocked_until']
    )

def add_blacklist(user_id: int, reason: Optional[str], blocked_until: Optional[int]) -> bool:
    # you can find collection's structure at line 4 (collection 1).
    coll = db.blacklist
    blacklist = coll.find_one({"user_id": str(user_id)})
    if blacklist is not None: return False
    coll.insert_one(
        {
            'user_id': str(user_id),
            'blocked_at': round(time.time()),
            'reason': reason,
            'blocked_until': blocked_until
        }
    )
    return True

def remove_blacklist(user_id: int) -> bool:
    # you can find collection's structure at line 4 (collection 1).
    coll = db.blacklist
    blacklist = coll.find_one({"user_id": str(user_id)})
    if blacklist is None: return False
    coll.delete_one({'user_id': str(user_id)})
    return True

def get_guild_user(guild_id: int, user_id: int) -> Optional[GuildUser]:
    coll = db.guild
    guild = coll.find_one({'guild_id': str(guild_id)})
    if guild is None: return None
    user = [memb for memb in guild['members'] if memb['user_id'] == str(user_id)]
    if len(user) == 0: return None
    user = user[0]
    return GuildUser(guild_id, user_id, user['balance'], user['xp'], user['level'])

def update_money(action: EditMoneyAction) -> bool:
    coll = db.guild
    guild_id = action.guild_id
    user_id = action.user_id
    amount = action.amount

    guild = coll.find_one({'guild_id': str(guild_id)})
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
                        'actions': [action.to_dict()]
                    }
                ],
                'autoroles': [],
                'buttonroles': []
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
                        'actions': [action.to_dict()]
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

def warn_user(action: UserWarn):
    coll = db.guild
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
                        'actions': {
                            {
                                'id': 4,
                                'user_id': str(user_id),
                                'mod_id': str(mod_id),
                                'time': round(time.time()),
                                'until': until,
                                'reason': reason
                            }
                        }
                    }
                ],
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
                        ]
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
    coll = db.guild
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
