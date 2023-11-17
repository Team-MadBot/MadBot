from . import mongo_db as db

from typing import Optional, List

def get_all_blacklist() -> List[dict]:
    coll = db.blacklist
    return list(coll.find())

def get_blacklist(resource_id: int) -> Optional[dict]:
    coll = db.blacklist
    return coll.find_one({"resource_id": str(resource_id)})

def add_blacklist(
    resource_id: int, 
    moderator_id: int,
    reason: Optional[str] = None,
    until: Optional[int] = None
) -> bool:
    coll = db.blacklist
    if get_blacklist(resource_id): # no dublicates
        return False
    coll.insert_one(
        {
            "resource_id": str(resource_id),
            "moderator_id": str(moderator_id),
            "reason": reason,
            "until": until
        }
    )
    return True

def remove_blacklist(resource_id: int) -> bool:
    coll = db.blacklist
    coll.delete_one({"resource_id": str(resource_id)})
    return True
