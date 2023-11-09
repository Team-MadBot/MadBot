from . import mongo_db as db

def add_voter(user_id: int) -> bool:
    """
    Add a voter.
    """
    coll = db.votes
    coll.insert_one(
        {
            "user_id": str(user_id)
        }
    )
    return True

def is_voted(user_id: int) -> bool:
    """
    Check if user has voted.
    """
    coll = db.votes
    return bool(coll.find_one({"user_id": str(user_id)}))
