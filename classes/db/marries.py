import time

from . import mongo_db as db
from motor import MotorCursor

from typing import (
    Optional,
    List
)

async def get_marries(guild_id: int, user_id: int) -> Optional[dict]:
    """
    Getting marries of user in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    - `user_id` - ID of the user.
    """
    coll = db.marries
    return await coll.find_one({'guild_id': guild_id, "$or": [{'user_id': user_id}, {'married_id': user_id}]})

def get_all_marries(guild_id: int) -> MotorCursor:
    """
    Getting all marries in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    """
    coll = db.marries
    return coll.find({'guild_id': guild_id})

async def marry(guild_id: int, user_id: int, married_id: int) -> bool:
    """
    Marry users in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    - `user_id` - ID of the user.
    - `married_id` - ID of the second user.
    """
    coll = db.marries
    if await coll.find_one(
        {'guild_id': guild_id, "$or": [{'married_id': user_id}]}
    ) is not None:
        return False
    await coll.insert_one({"guild_id": guild_id, "user_id": user_id, "married_id": married_id, 'dt': round(time.time())})
    return True

async def divorce(guild_id: int, user_id: int) -> bool:
    """
    Divorce user in the guild.

    Arguments:
    - `guild_id` - ID of the guild where to find.
    - `user_id` - ID of the user.
    """
    coll = db.marries
    marries = await coll.find_one({'guild_id': guild_id, "$or": [{'user_id': user_id}, {'married_id': user_id}]})
    if not marries: return False
    await coll.delete_one({"guild_id": guild_id, "$or": [{"user_id": user_id}, {"married_id": user_id}]})
    return True