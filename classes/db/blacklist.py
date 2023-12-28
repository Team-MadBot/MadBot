from typing import Optional

from . import mongo_db as db


def get_all_blacklist():
    coll = db.blacklist
    return coll.find()

async def get_blacklist(resource_id: int) -> Optional[dict]:
    coll = db.blacklist
    return await coll.find_one({"resource_id": str(resource_id)})

async def add_blacklist(
    resource_id: int, 
    moderator_id: int,
    reason: Optional[str] = None,
    until: Optional[int] = None
) -> bool:
    coll = db.blacklist
    if await get_blacklist(resource_id): # no dublicates
        return False
    await coll.insert_one(
        {
            "resource_id": str(resource_id),
            "moderator_id": str(moderator_id),
            "reason": reason,
            "until": until
        }
    )
    return True

async def remove_blacklist(resource_id: int) -> bool:
    coll = db.blacklist
    await coll.delete_one({"resource_id": str(resource_id)})
    return True
