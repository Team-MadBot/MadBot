from . import mongo_db as db

from typing import Optional


async def get_shutted_command(command: str) -> Optional[dict]:
    coll = db.shutted_commands
    return await coll.find_one({"command": command})


async def add_shutted_command(command: str, reason: Optional[str] = None) -> bool:
    coll = db.shutted_commands
    if await get_shutted_command(command):  # no dublicates
        return False
    await coll.insert_one({"command": command, "reason": reason})
    return True


async def remove_shutted_command(command: str) -> bool:
    coll = db.shutted_commands
    await coll.delete_one({"command": command})
    return True
