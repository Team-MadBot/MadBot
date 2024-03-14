from typing import Optional

from . import mongo_db as db

async def get_guild_autorole(guild_id: int) -> Optional[int]:
    """
    Gets info about autorole in the guild.

    Arguments:
    - `guild_id` - ID of the guild.

    Returns:
    - ID of the role, if any.
    """
    coll = db.autorole
    autorole = await coll.find_one({'guild_id': str(guild_id)})
    if autorole is not None:
        autorole = int(autorole['role_id'])
    return autorole

async def add_guild_autorole(guild_id: int, role_id: int) -> bool:
    """
    Adds autorole to the guild.

    Arguments:
    - `guild_id` - ID of the guild.
    - `role_id` - ID of the role.
    """
    coll = db.autorole
    await coll.insert_one({'guild_id': str(guild_id), 'role_id': str(role_id)})
    return True

async def delete_guild_autorole(guild_id: int) -> bool:
    """
    Deletes autorole from the guild.

    Arguments:
    - `guild_id` - ID of the guild.
    """
    coll = db.autorole
    await coll.delete_one({'guild_id': str(guild_id)})
    return True

async def update_guild_autorole(guild_id: int, role_id: int) -> bool:
    """
    Updates autorole in the guild.

    Arguments:
    - `guild_id` - ID of the guild.
    - `role_id` - ID of the new role.
    """
    coll = db.autorole
    await coll.update_one({'guild_id': str(guild_id)}, {"$set": {'role_id': str(role_id)}})
    return True

def get_all_autoroles():
    """
    Gets all autoroles, if any.
    """
    coll = db.autorole
    return coll.find()
