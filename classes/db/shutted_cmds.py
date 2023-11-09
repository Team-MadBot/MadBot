from . import db

from typing import Optional

def get_shutted_command(command: str) -> Optional[dict]:
    coll = db.shutted_commands
    return coll.find_one({"command": command})

def add_shutted_command(
    command: str, 
    reason: Optional[str] = None
) -> bool:
    coll = db.shutted_commands
    if get_shutted_command(command): # no dublicates
        return False
    coll.insert_one(
        {
            "command": command,
            "reason": reason
        }
    )
    return True

def remove_shutted_command(command: str) -> bool:
    coll = db.shutted_commands
    coll.delete_one({"command": command})
    return True
