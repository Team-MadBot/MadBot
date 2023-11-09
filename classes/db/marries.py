import time

from . import mongo_db as db

from typing import (
    Optional,
    List
)

def get_marries(guild_id: int, user_id: int) -> Optional[dict]:
    """
    Getting marries of user in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    - `user_id` - ID of the user.
    """
    coll = db.marries
    return coll.find_one({'guild_id': guild_id, "$or": [{'user_id': user_id}, {'married_id': user_id}]})

def get_all_marries(guild_id: int) -> Optional[List[dict]]:
    """
    Getting all marries in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    """
    coll = db.marries
    if coll.count_documents({'guild_id': guild_id}) == 0: return None
    return coll.find({'guild_id': guild_id})

def marry(guild_id: int, user_id: int, married_id: int) -> bool:
    """
    Marry users in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    - `user_id` - ID of the user.
    - `married_id` - ID of the second user.
    """
    coll = db.marries
    marries = coll.find_one({'guild_id': guild_id, "$or": [{'user_id': user_id, 'user_id': married_id}], "$or": [{'married_id': married_id, 'married_id': user_id}]})
    if marries: return False
    coll.insert_one({"guild_id": guild_id, "user_id": user_id, "married_id": married_id, 'dt': round(time.time())})
    return True

def divorce(guild_id: int, user_id: int) -> bool:
    """
    Divorce user in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    - `user_id` - ID of the user.
    """
    coll = db.marries
    marries = coll.find_one({'guild_id': guild_id, "$or": [{'user_id': user_id}, {'married_id': user_id}]})
    if not marries: return False
    coll.delete_one({"guild_id": guild_id, "$or": [{"user_id": user_id}, {"married_id": user_id}]})
    return True