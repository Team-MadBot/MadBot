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

3. GuildItem:
{
    'id': int,
    'name': str,
    'cost': int,
    'description': str,
    'req_role': Optional[str]
}

4. GuildMember:
{
    'user_id': str,
    'balance': int,
    'level': int,
    'xp': int,
    'actions': List[GuildMemberAction]
    'inventory': List[GuildItem]
}

5. ButtonRole:
{
    'channel_id': str,
    'message_id': str,
    'type': str in ("single", "multiple")
    'roles': List[str]
}

6. Guild:
{
    'guild_id': str,
    'members': List[GuildMember],
    'autoroles': List[str],
    'buttonroles': List[ButtonRole],
    'items': List[GuildItem]
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
from tools.models import GuildItem
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
    return GuildUser(
        guild_id, 
        user_id, 
        user['balance'], 
        user['xp'], 
        user['level'], 
        [GuildItem.from_dict(guild_id, item) for item in user['inventory']]
    )

def update_money(action: EditMoneyAction) -> bool:
    coll = db.guild
    guild_id = action.guild_id
    amount = action.amount

    guild = coll.find_one({'guild_id': str(guild_id)})
    if action.id == models.GuildActionsType.TRANSFER:
        if guild is None:
            return False
        
        from_id = action.from_id
        to_id = action.to_id

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

def add_guild_item(item: models.GuildItem) -> bool:
    """
    Добавляет предмет в магазин сервера.

    Параметры:
    item (models.GuildItem): Объект предмета сервера. Содержит:
    - guild_id (int): ID сервера
    - name (str): Название предмета
    - cost (int): Цена предмета
    - description (str): Описание предмета
    - req_role (Optional[int]): Необходимая роль для покупки предмета

    Функциональность:
    - Проверяет, есть ли запись о сервере в базе данных. Если нет, создает новую запись.
    - Добавляет предмет в список предметов сервера.
    - Возвращает True в случае успеха, иначе False.
    """
    coll = db.guild
    guild_id = item.guild_id
    name = item.name
    cost = item.cost
    description = item.description
    req_role = item.req_role
    if req_role is not None: req_role = str(req_role)

    guild = coll.find_one({'guild_id': str(guild_id)})
    if guild is None:
        coll.insert_one(
            {
                'guild_id': str(guild_id),
                'members': [],
                'autoroles': [],
                'buttonroles': [],
                'items': [
                    {
                        'name': name,
                        'cost': cost,
                        'description': description,
                        'req_role': req_role
                    }
                ]
                
            }
        )
        return True
    
    coll.update_one(
        {'guild_id': str(guild_id)},
        {
            '$push': {
                "items": {
                    'name': name,
                    'cost': cost,
                    'description': description,
                    'req_role': req_role
                }
            }
        }
    )
    return True

def get_guild(guild_id: int) -> models.BotGuild:
    coll = db.guild

    