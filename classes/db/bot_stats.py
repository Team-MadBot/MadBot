from . import db

def get_bot_stats() -> dict:
    coll = db.bot_stats
    return coll.find_one({})

def update_used_commands() -> bool:
    coll = db.bot_stats
    coll.update_one(
        {},
        {
            "$inc": {
                "used_commands": 1
            }
        }
    )
    return True

def update_last_command(last_command: str) -> bool:
    coll = db.bot_stats
    coll.update_one(
        {},
        {
            "$set": {
                "last_command": last_command
            }
        }
    )
    return True

def create_bot_stats() -> bool: # for debug purposes
    coll = db.bot_stats
    if coll.find_one() is not None:
        return False
    coll.insert_one(
        {
            "last_command": None,
            "used_commands": 0
        }
    )
    return True
