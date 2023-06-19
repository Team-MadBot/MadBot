import time

from . import database
from typing import Optional
from tools.models import BlackList

def check_blacklist(user_id: int) -> bool:
    # you can find collection's structure at line 4 (collection 1) in __init__.py.
    coll = database.blacklist
    return bool(coll.find_one({"user_id": str(user_id)}))

def get_blacklist(user_id: int) -> Optional[BlackList]:
    # you can find collection's structure at line 4 (collection 1) in __init__.py.
    coll = database.blacklist
    blacklist = coll.find_one({"user_id": str(user_id)})
    if blacklist is None: return None
    return BlackList(
        int(blacklist['user_id']), 
        blacklist['blocked_at'],
        blacklist['reason'],
        blacklist['blocked_until']
    )

def add_blacklist(user_id: int, reason: Optional[str], blocked_until: Optional[int]) -> bool:
    # you can find collection's structure at line 4 (collection 1) in __init__.py.
    coll = database.blacklist
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
    # you can find collection's structure at line 4 (collection 1) in __init__.py.
    coll = database.blacklist
    blacklist = coll.find_one({"user_id": str(user_id)})
    if blacklist is None: return False
    coll.delete_one({'user_id': str(user_id)})
    return True